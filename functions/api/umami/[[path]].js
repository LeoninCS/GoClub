// 同源代理：把 /api/umami/* 转发到 Umami share API。
// 用途：浏览器直连 cloud.umami.is 被广告拦截 / 网络拦截时，
// 浏览器只和本站同源通信即可拿到数据（无跨域预检、不触发拦截规则）。
// 注意：仅在 Cloudflare Pages 上生效；GitHub Pages 会忽略 functions/
// 目录，那时客户端走直连（见 umami-stats.html 的 fetchApi 回退）。
export async function onRequest(context) {
  const { request, params } = context;

  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'x-umami-share-token, x-umami-share-context, content-type',
        'Access-Control-Max-Age': '86400'
      }
    });
  }

  const url = new URL(request.url);
  const segments = params.path || [];
  const target =
    'https://cloud.umami.is/analytics/us/api/' + segments.join('/') + url.search;

  const headers = new Headers(request.headers);
  headers.delete('host');

  const res = await fetch(target, {
    method: request.method,
    headers: headers,
    redirect: 'follow'
  });

  const outHeaders = new Headers(res.headers);
  outHeaders.set('Access-Control-Allow-Origin', '*');
  return new Response(res.body, { status: res.status, headers: outHeaders });
}
