
document.addEventListener("DOMContentLoaded", function () {
  backToMainPage();
});
function backToMainPage() {
  const titleElement = document.getElementById("title");
  titleElement.addEventListener("click", function () {
    window.location.href = "/";
  });
}