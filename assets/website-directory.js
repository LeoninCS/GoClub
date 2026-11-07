const directory = document.querySelector(".website-directory");
const filters = directory.querySelector(".website-filters");
const buttons = filters.querySelectorAll("button");
const groups = directory.querySelectorAll(".website-group");

filters.hidden = false;
filters.addEventListener("click", (event) => {
  const selected = event.target.closest("button");
  if (!selected) return;

  for (const button of buttons) {
    button.setAttribute("aria-pressed", String(button === selected));
  }
  for (const group of groups) {
    group.hidden = Boolean(selected.dataset.group) && group.dataset.group !== selected.dataset.group;
  }
});
