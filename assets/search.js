'use strict';

{{ $searchDataFile := printf "%s.search-data.json" .Language.Name }}
{{ $searchData := resources.Get "search-data.json" | resources.ExecuteAsTemplate $searchDataFile . | resources.Minify | resources.Fingerprint }}
{{ $searchConfig := i18n "bookSearchConfig" | default "{}" }}

(function () {
  const searchDataURL = '{{ partial "docs/links/resource-precache" $searchData }}';
  const indexConfig = Object.assign({{ $searchConfig }}, {
    includeScore: true,
    useExtendedSearch: true,
    fieldNormWeight: 1.5,
    threshold: 0.2,
    ignoreLocation: true,
    keys: [
      { name: 'title', weight: 0.4 },
      { name: 'aliases', weight: 0.15 },
      { name: 'headings', weight: 0.15 },
      { name: 'description', weight: 0.1 },
      { name: 'content', weight: 0.2 }
    ]
  });

  const input = document.querySelector('#book-search-input');
  const status = document.querySelector('#book-search-status');
  const results = document.querySelector('#book-search-results');
  const closeButton = document.querySelector('#book-search-close');
  const clearButton = document.querySelector('#book-search-clear');
  const backdrop = document.querySelector('#book-search-backdrop');
  const searchPanel = document.querySelector('.book-search');
  const resultPageSize = 10;
  const autoLoadThreshold = 160;
  const searchHistoryKey = 'goclubSearch';
  const searchSessionKey = 'goclubLastSearch';
  let searchIndex = null;
  let searchPromise = null;
  let debounceTimer = null;
  let currentSearchHits = [];
  let visibleResultCount = 0;
  let panelPlaceholder = null;
  let backdropPlaceholder = null;
  let pendingRestoreState = null;
  let autoLoadFrame = null;
  let persistFrame = null;
  let suppressLastSearchRestore = false;

  scheduleSearchContextHighlight();

  if (!input || !status || !results || !closeButton || !clearButton || !backdrop
    || !searchPanel) {
    return;
  }

  panelPlaceholder = document.createComment('book-search-panel');
  backdropPlaceholder = document.createComment('book-search-backdrop');
  searchPanel.parentNode.insertBefore(panelPlaceholder, searchPanel);
  backdrop.parentNode.insertBefore(backdropPlaceholder, backdrop);

  input.addEventListener('focus', init);
  input.addEventListener('click', restoreLastSearchState);
  input.addEventListener('click', openSearchPanel);
  input.addEventListener('input', scheduleSearch);
  input.addEventListener('input', openSearchPanel);
  results.addEventListener('scroll', handleResultsScroll, { passive: true });
  closeButton.addEventListener('click', closeSearchPanel);
  backdrop.addEventListener('click', closeSearchPanel);
  clearButton.addEventListener('click', clearSearch);
  document.addEventListener('keypress', focusSearchFieldOnKeyPress);
  document.addEventListener('keydown', closeSearchPanelOnEscape);
  window.addEventListener('pagehide', persistSearchState);
  window.addEventListener('pageshow', restoreSearchPanelFromPageCache);

  pendingRestoreState = readSearchState();
  if (pendingRestoreState) {
    input.value = pendingRestoreState.query;
    clearButton.classList.remove('hidden');
    if (pendingRestoreState.panelOpen) {
      openSearchPanel();
    }
    init();
  }

  function focusSearchFieldOnKeyPress(event) {
    if (event.target.value !== undefined || input === document.activeElement) {
      return;
    }

    const characterPressed = String.fromCharCode(event.charCode);
    const dataHotkeys = input.getAttribute('data-hotkeys') || '';
    if (dataHotkeys.indexOf(characterPressed) < 0) {
      return;
    }

    input.focus();
    event.preventDefault();
  }

  function init() {
    if (searchIndex || searchPromise) {
      return searchPromise;
    }

    input.required = true;
    setStatus('正在加载搜索索引…', 'loading');

    searchPromise = fetch(searchDataURL)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Search index request failed: ${response.status}`);
        }
        return response.json();
      })
      .then(pages => {
        searchIndex = new Fuse(pages, indexConfig);
        input.required = false;
        searchPromise = null;
        const restoreState = pendingRestoreState;
        pendingRestoreState = null;
        if (restoreState && restoreState.query === input.value.trim()) {
          search(restoreState);
        } else if (input.value.trim()) {
          search();
        } else {
          clearStatus();
        }
      })
      .catch(error => {
        console.error(error);
        input.required = false;
        searchPromise = null;
        setStatus('搜索索引加载失败，请重新聚焦搜索框重试。', 'error');
      });

    return searchPromise;
  }

  function scheduleSearch() {
    suppressLastSearchRestore = false;
    clearButton.classList.toggle('hidden', !input.value);
    window.clearTimeout(debounceTimer);
    debounceTimer = window.setTimeout(function () {
      search();
    }, 250);
  }

  function openSearchPanel() {
    searchPanel.classList.remove('is-results-collapsed');
    if (searchPanel.parentNode !== document.body) {
      document.body.appendChild(backdrop);
      document.body.appendChild(searchPanel);
    }
    searchPanel.classList.add('is-expanded');
    backdrop.classList.remove('hidden');
    document.body.classList.add('search-overlay-open');
  }

  function closeSearchPanel() {
    searchPanel.classList.remove('is-expanded');
    searchPanel.classList.toggle('is-results-collapsed', Boolean(input.value.trim()));
    backdrop.classList.add('hidden');
    document.body.classList.remove('search-overlay-open');
    if (panelPlaceholder.parentNode) {
      panelPlaceholder.parentNode.insertBefore(searchPanel, panelPlaceholder.nextSibling);
    }
    if (backdropPlaceholder.parentNode) {
      backdropPlaceholder.parentNode.insertBefore(backdrop, backdropPlaceholder.nextSibling);
    }
    persistSearchState();
  }

  function closeSearchPanelOnEscape(event) {
    if (event.key !== 'Escape' || !searchPanel.classList.contains('is-expanded')) {
      return;
    }

    closeSearchPanel();
    input.blur();
  }

  function clearSearch() {
    suppressLastSearchRestore = true;
    input.value = '';
    searchPanel.classList.remove('is-results-collapsed');
    clearButton.classList.add('hidden');
    search();
    clearSearchState();
    input.focus();
  }

  function search(restoreState) {
    const query = input.value.trim();
    clearResults();
    currentSearchHits = [];
    visibleResultCount = 0;

    if (!query) {
      clearStatus();
      clearSearchState();
      return;
    }

    if (!searchIndex) {
      setStatus('正在加载搜索索引…', 'loading');
      init();
      return;
    }

    const searchHits = searchIndex.search(query);
    currentSearchHits = rankSearchHits(filterExactDateHits(searchHits, query));
    if (!currentSearchHits.length) {
      setStatus(`没有找到与“${query}”相关的内容。`, 'empty');
      persistSearchState();
      return;
    }

    const restoredCount = restoreState && Number(restoreState.visibleResultCount);
    showMoreResults(Number.isFinite(restoredCount) && restoredCount > 0
      ? restoredCount
      : resultPageSize);
    if (restoreState) {
      window.requestAnimationFrame(function () {
        results.scrollTop = Math.max(0, Number(restoreState.resultsScrollTop) || 0);
        persistSearchState();
      });
    }
  }

  function rankSearchHits(searchHits) {
    return searchHits
      .map((hit, originalIndex) => {
        const priorityFactor = contentPriorityFactor(hit.item);
        return {
          hit,
          originalIndex,
          priorityFactor,
          adjustedScore: (hit.score === undefined ? 1 : hit.score) * priorityFactor
        };
      })
      .sort((left, right) => {
        return left.adjustedScore - right.adjustedScore
          || left.priorityFactor - right.priorityFactor
          || (left.hit.score || 0) - (right.hit.score || 0)
          || left.originalIndex - right.originalIndex;
      })
      .map(entry => entry.hit);
  }

  function filterExactDateHits(searchHits, query) {
    if (!/^\d{4}[.-]\d{2}[.-]\d{2}$/.test(query)) {
      return searchHits;
    }

    const normalizedDate = query.replace(/-/g, '.');
    return searchHits.filter(hit => {
      const breadcrumb = Array.isArray(hit.item.breadcrumb) ? hit.item.breadcrumb : [];
      return breadcrumb.some(part => part === normalizedDate);
    });
  }

  function contentPriorityFactor(page) {
    const href = page.href || '';
    if (page.category === '八股总结' || href.indexOf('/docs/baguwen/') === 0) {
      return 0.72;
    }
    if (page.type === 'interview' || href.indexOf('/docs/interview/') === 0) {
      return 0.78;
    }
    if (page.type === 'article') {
      return 0.9;
    }
    if (page.type === 'book') {
      return 1.15;
    }
    return 1;
  }

  function showMoreResults(targetVisibleCount) {
    const query = input.value.trim();
    const requestedCount = Number.isFinite(targetVisibleCount)
      ? Math.max(visibleResultCount, targetVisibleCount)
      : visibleResultCount + resultPageSize;
    const nextVisibleCount = Math.min(requestedCount, currentSearchHits.length);
    currentSearchHits
      .slice(visibleResultCount, nextVisibleCount)
      .forEach(hit => results.appendChild(renderResult(hit.item, query)));
    visibleResultCount = nextVisibleCount;
    setStatus(`找到 ${currentSearchHits.length} 条结果，当前显示 ${visibleResultCount} 条。`, 'ready');
    persistSearchState();
  }

  function handleResultsScroll() {
    schedulePersistSearchState();
    if (autoLoadFrame || visibleResultCount >= currentSearchHits.length) {
      return;
    }

    const distanceFromBottom = results.scrollHeight - results.scrollTop - results.clientHeight;
    if (distanceFromBottom > autoLoadThreshold) {
      return;
    }

    autoLoadFrame = window.requestAnimationFrame(function () {
      autoLoadFrame = null;
      showMoreResults();
    });
  }

  function schedulePersistSearchState() {
    if (persistFrame) {
      return;
    }
    persistFrame = window.requestAnimationFrame(function () {
      persistFrame = null;
      persistSearchState();
    });
  }

  function persistSearchState() {
    const query = input.value.trim();
    if (!query) {
      return;
    }

    const searchState = {
      path: window.location.pathname,
      query: query,
      visibleResultCount: visibleResultCount,
      resultsScrollTop: results.scrollTop,
      panelOpen: searchPanel.classList.contains('is-expanded')
    };
    const currentState = window.history.state && typeof window.history.state === 'object'
      ? window.history.state
      : {};
    window.history.replaceState(Object.assign({}, currentState, {
      [searchHistoryKey]: searchState
    }), '');
    try {
      window.sessionStorage.setItem(searchSessionKey, JSON.stringify(searchState));
    } catch (error) {
      // Search history restoration remains available when session storage is blocked.
    }
  }

  function readSearchState() {
    const state = window.history.state && window.history.state[searchHistoryKey];
    if (!state || state.path !== window.location.pathname || typeof state.query !== 'string'
      || !state.query.trim()) {
      return null;
    }
    return state;
  }

  function readLastSearchState() {
    try {
      const state = JSON.parse(window.sessionStorage.getItem(searchSessionKey));
      if (state && typeof state.query === 'string' && state.query.trim()) {
        return state;
      }
    } catch (error) {
      // Fall back to the query carried by search-result links.
    }

    const query = new URLSearchParams(window.location.search).get('search');
    return query && query.trim()
      ? { query: query, visibleResultCount: resultPageSize, resultsScrollTop: 0 }
      : null;
  }

  function restoreLastSearchState() {
    if (suppressLastSearchRestore || input.value.trim()) {
      return;
    }
    const state = readLastSearchState();
    if (!state) {
      return;
    }

    input.value = state.query;
    clearButton.classList.remove('hidden');
    pendingRestoreState = state;
    if (searchIndex) {
      pendingRestoreState = null;
      search(state);
    }
  }

  function clearSearchState() {
    if (window.history.state && window.history.state[searchHistoryKey]) {
      const nextState = Object.assign({}, window.history.state);
      delete nextState[searchHistoryKey];
      window.history.replaceState(nextState, '');
    }
    try {
      window.sessionStorage.removeItem(searchSessionKey);
    } catch (error) {
      // Ignore storage restrictions; the visible search state has still been cleared.
    }
  }

  function restoreSearchPanelFromPageCache(event) {
    if (!event.persisted) {
      return;
    }
    const state = readSearchState();
    if (!state) {
      return;
    }
    if (state.panelOpen) {
      openSearchPanel();
    }
    window.requestAnimationFrame(function () {
      results.scrollTop = Math.max(0, Number(state.resultsScrollTop) || 0);
    });
  }

  function renderResult(page, query) {
    const item = document.createElement('li');
    item.className = 'book-search-result';

    const link = document.createElement('a');
    link.href = addSearchContext(page.href, query);
    link.addEventListener('click', persistSearchState);

    const heading = document.createElement('span');
    heading.className = 'book-search-result-heading';

    const badge = document.createElement('span');
    badge.className = `book-search-result-badge is-${page.type || 'article'}`;
    badge.textContent = resultTypeLabel(page.type);

    const title = document.createElement('strong');
    title.className = 'book-search-result-title';
    appendHighlightedText(title, page.title, query);

    heading.appendChild(badge);
    heading.appendChild(title);
    link.appendChild(heading);

    const breadcrumb = document.createElement('span');
    breadcrumb.className = 'book-search-result-breadcrumb';
    const breadcrumbParts = Array.isArray(page.breadcrumb) ? page.breadcrumb : [];
    breadcrumb.textContent = breadcrumbParts.length ? breadcrumbParts.join(' › ') : page.category || page.section;
    link.appendChild(breadcrumb);

    const snippet = document.createElement('small');
    snippet.className = 'book-search-result-snippet';
    appendHighlightedText(snippet, makeSnippet(page, query), query);
    link.appendChild(snippet);

    item.appendChild(link);
    return item;
  }

  function resultTypeLabel(type) {
    return {
      book: '书籍章节',
      interview: '面试',
      section: '栏目',
      article: '文章'
    }[type] || '文章';
  }

  function makeSnippet(page, query) {
    const preferred = (page.content || page.description || '').replace(/\s+/g, ' ').trim();
    if (!preferred) {
      return '';
    }

    const terms = queryTerms(query);
    const lower = preferred.toLocaleLowerCase();
    const positions = terms
      .map(term => lower.indexOf(term.toLocaleLowerCase()))
      .filter(position => position >= 0);
    const matchAt = positions.length ? Math.min.apply(null, positions) : 0;
    const start = Math.max(0, matchAt - 42);
    const end = Math.min(preferred.length, matchAt + 118);
    return `${start > 0 ? '…' : ''}${preferred.slice(start, end)}${end < preferred.length ? '…' : ''}`;
  }

  function addSearchContext(href, query) {
    const url = new URL(href, window.location.origin);
    url.searchParams.set('search', query);
    return `${url.pathname}${url.search}${url.hash}`;
  }

  function appendHighlightedText(container, text, query) {
    const terms = queryTerms(query).sort((left, right) => right.length - left.length);
    if (!terms.length) {
      container.textContent = text;
      return;
    }

    const pattern = new RegExp(`(${terms.map(escapeRegExp).join('|')})`, 'gi');
    text.split(pattern).forEach(part => {
      if (terms.some(term => term.toLocaleLowerCase() === part.toLocaleLowerCase())) {
        const mark = document.createElement('mark');
        mark.textContent = part;
        container.appendChild(mark);
      } else {
        container.appendChild(document.createTextNode(part));
      }
    });
  }

  function queryTerms(query) {
    const normalizedQuery = query.trim();
    const terms = normalizedQuery.split(/\s+/).map(term => term.trim()).filter(Boolean);
    return terms.length > 1 ? [normalizedQuery].concat(terms) : terms;
  }

  function escapeRegExp(value) {
    return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function setStatus(message, state) {
    status.textContent = message;
    status.className = `book-search-status is-${state}`;
  }

  function clearStatus() {
    status.textContent = '';
    status.className = 'book-search-status hidden';
  }

  function clearResults() {
    while (results.firstChild) {
      results.removeChild(results.firstChild);
    }
  }

  function scheduleSearchContextHighlight() {
    const run = function () {
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(highlightSearchContext);
      });
    };

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', run, { once: true });
    } else {
      run();
    }
  }

  function highlightSearchContext() {
    const query = new URLSearchParams(window.location.search).get('search');
    const article = document.querySelector('.book-page article.book-article');
    if (!query || !article) {
      return;
    }

    const terms = queryTerms(query).sort((left, right) => right.length - left.length);
    if (!terms.length) {
      return;
    }

    const pattern = new RegExp(`(${terms.map(escapeRegExp).join('|')})`, 'gi');
    const walker = document.createTreeWalker(article, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        const parent = node.parentElement;
        if (!parent || !node.nodeValue.trim()
          || parent.closest('script, style, noscript, mark.goclub-search-hit, a.anchor')) {
          return NodeFilter.FILTER_REJECT;
        }
        pattern.lastIndex = 0;
        const matches = pattern.test(node.nodeValue);
        pattern.lastIndex = 0;
        return matches ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      }
    });
    const matchingNodes = [];
    while (walker.nextNode()) {
      matchingNodes.push(walker.currentNode);
    }

    matchingNodes.forEach(node => highlightTextNode(node, pattern, terms));

    const fragmentTarget = document.querySelector(':target');
    const preferredHit = findPreferredHit(fragmentTarget, article, query)
      || findExactHit(article, query)
      || article.querySelector('mark.goclub-search-hit');
    const scrollTarget = preferredHit || fragmentTarget;
    if (!scrollTarget) {
      return;
    }

    const collapsedAnswer = scrollTarget.closest('details:not([open])');
    if (collapsedAnswer) {
      collapsedAnswer.open = true;
    }
    if (preferredHit) {
      preferredHit.classList.add('is-current');
    }
    if ('scrollRestoration' in window.history) {
      window.history.scrollRestoration = 'manual';
    }
    window.setTimeout(function () {
      const targetRect = scrollTarget.getBoundingClientRect();
      const targetTop = window.scrollY + targetRect.top
        - (window.innerHeight / 2)
        + (targetRect.height / 2);
      window.scrollTo({ top: Math.max(0, targetTop), behavior: 'auto' });
    }, 220);
  }

  function highlightTextNode(node, pattern, terms) {
    const fragment = document.createDocumentFragment();
    node.nodeValue.split(pattern).forEach(part => {
      if (terms.some(term => term.toLocaleLowerCase() === part.toLocaleLowerCase())) {
        const mark = document.createElement('mark');
        mark.className = 'goclub-search-hit';
        mark.textContent = part;
        fragment.appendChild(mark);
      } else {
        fragment.appendChild(document.createTextNode(part));
      }
    });
    node.parentNode.replaceChild(fragment, node);
  }

  function findPreferredHit(fragmentTarget, article, query) {
    if (!fragmentTarget || !article.contains(fragmentTarget)) {
      return null;
    }

    const targetLevel = headingLevel(fragmentTarget);
    const hits = [];
    let element = fragmentTarget;
    while (element) {
      if (element !== fragmentTarget && targetLevel && headingLevel(element) <= targetLevel) {
        break;
      }
      if (element.matches && element.matches('mark.goclub-search-hit')) {
        hits.push(element);
      }
      if (element.querySelectorAll) {
        hits.push.apply(hits, element.querySelectorAll('mark.goclub-search-hit'));
      }
      element = element.nextElementSibling;
    }
    return hits.find(hit => hit.textContent.toLocaleLowerCase() === query.toLocaleLowerCase())
      || hits[0]
      || null;
  }

  function findExactHit(container, query) {
    return Array.from(container.querySelectorAll('mark.goclub-search-hit'))
      .find(hit => hit.textContent.toLocaleLowerCase() === query.toLocaleLowerCase())
      || null;
  }

  function headingLevel(element) {
    const match = element && /^H([1-6])$/.exec(element.tagName);
    return match ? Number(match[1]) : 0;
  }
})();
