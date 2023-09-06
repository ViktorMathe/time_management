let toastElList = [].slice.call(document.querySelectorAll('.toast'))
let toastList = toastElList.map(function (toastEl) {
    let option = {
        animation: true,
        autohide: true,
        delay: 5000,
    }
  let bsToast = new bootstrap.Toast(toastEl, option)
  bsToast.show();
});

$(function () {
  $("#tabs").tabs();
});
$('#date_to').datepicker({ "dateFormat": "yy-mm-dd" });
$('#date_from').datepicker({ "dateFormat": "yy-mm-dd" });
$('#time_to').timepicker({ 'timeFormat': 'H:i' });
$('#time_from').timepicker({ 'timeFormat': 'H:i' });