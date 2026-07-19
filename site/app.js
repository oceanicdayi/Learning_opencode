function getCodeText(targetId) {
  const target = document.getElementById(targetId);
  if (!target) return "";
  return target.textContent.trim();
}

async function copyCode(button) {
  const targetId = button.dataset.copy;
  const text = getCodeText(targetId);
  if (!text) return;

  const originalLabel = button.textContent;
  try {
    await navigator.clipboard.writeText(text);
    button.textContent = "已複製";
    button.classList.add("done");
  } catch (error) {
    console.error("Clipboard API unavailable", error);
    const range = document.createRange();
    const selection = window.getSelection();
    const target = document.getElementById(targetId);
    range.selectNodeContents(target);
    selection.removeAllRanges();
    selection.addRange(range);
    button.textContent = "請手動複製";
  }

  window.setTimeout(() => {
    button.textContent = originalLabel;
    button.classList.remove("done");
  }, 1800);
}

function initializeCopyButtons() {
  document.querySelectorAll("[data-copy]").forEach((button) => {
    button.addEventListener("click", () => copyCode(button));
  });
}

document.addEventListener("DOMContentLoaded", initializeCopyButtons);
