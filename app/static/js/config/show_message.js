function show_msg_success(elId, message) {
  let html = `
    <div class="alert alert-success solid alert-right-icon alert-dismissible fade show" role="alert">
        <span><i class="mdi mdi-check"></i></span>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        <strong>Success!</strong> ${message}
    </div>
    `;
  $(elId).html(html);

  // Tự động ẩn sau 3 giây
  setTimeout(function () {
    remove_msg(elId);
  }, 3000);
}

function remove_msg(elId) {
  $(elId).html("");
}

function show_toastr(message, type = "success") {
  toastr.options = {
    closeButton: true,
    progressBar: true,
    positionClass: "toast-top-right",
    timeOut: "3000",
  };
  toastr[type](message);
}
