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

document.addEventListener('DOMContentLoaded', function () {
  var company_id = getQueryParameterByName('company_id');
  // Rest of your JavaScript code

  if (company_id) {
    // Send the 'company_id' to your server using AJAX
    // Example using fetch:
    fetch('/manager-registration/' + company_id + '/', {  // Adjust the endpoint
      method: 'POST',
      body: JSON.stringify({ company_id }),
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then(response => response.json())
      .then(data => {
        // Handle the server's response here
      })
      .catch(error => {
        console.error('Error:', error);
      });
  }
});