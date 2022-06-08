function snackbar() {
  var snack = document.getElementById("snackbar_positive");
  if (!snack) {
    var snack = document.getElementById("snackbar_error");
  }
  if (!snack) {
    var snack = document.getElementById("snackbar_info");
  }
  if (!snack) {
    var snack = document.getElementById("snackbar_");
    snack.setAttribute("id", "snackbar_positive");
  }
  if (snack.textContent) {
    snack.className = "show";

    // After 3 seconds, remove the show class from DIV
    setTimeout(function () {
      snack.className = snack.className.replace("show", "");
    }, 3000);
  }
}
