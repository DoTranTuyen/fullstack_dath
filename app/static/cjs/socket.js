function displayNotification(message, level = "info") {
  toastr.options = {
    closeButton: true,
    progressBar: true,
    newestOnTop: true,
    timeOut: 4000,
    extendedTimeOut: 1000,
    positionClass: "toast-top-right",
    preventDuplicates: true,
    showEasing: "swing",
    hideEasing: "linear",
    showMethod: "fadeIn",
    hideMethod: "fadeOut",
  };
  const toastrMap = {
    success: () => toastr.success(message),
    error: () => toastr.error(message),
    warning: () => toastr.warning(message,),
    info: () => toastr.info(message),
    payment: () => toastr.info(message)
  };

  const notify = toastrMap[level] || toastrMap["info"];
  notify();
}

socket.onmessage = function (event) {
  const data = JSON.parse(event.data);
  const message = data.message;
  const level = data.level;
  displayNotification(message, level);
  load_notification_list();
};

function socket_update_order_status_detail(type, product_name ='',table_id, status='') {
  if (socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({
        type:type,
        product_name: product_name,
        table_id: table_id,
        product_status: status,
    }));
  }
}
