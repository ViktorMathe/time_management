let toastElList = [].slice.call(document.querySelectorAll('.toast'))
let toastList = toastElList.map(function (toastEl) {
    let option = {
        animation: true,
        autohide: true,
        delay: 5000,
    }
  let bsToast = new bootstrap.Toast(toastEl, option)
  bsToast.show();
})