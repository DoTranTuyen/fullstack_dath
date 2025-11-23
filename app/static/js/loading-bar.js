// ================================================
// Disable, Enable item
// ================================================
function disable_element(e) {
  var exist = e.find(".sk-three-bounce").length;

  if (!exist) {
    //1)Disable đi không cho bấm vào
    e.css({ "pointer-events": "none", position: "relative" });
    spinner =
      '<div class="sk-three-bounce d-flex align-items-center">' +
      '<div class="sk-child sk-bounce1" style="margin-left: calc(50% - 30px); background:#EA7A9A"></div>' +
      '<div class="sk-child sk-bounce2" style="background: #EA7A9A"></div>' +
      '<div class="sk-child sk-bounce3" style="background: #EA7A9A"></div>' +
      "</div>";

    e_width = e.width();
    e_height = e.height();

    //2)Thêm spinner
    e.append(spinner);
    $spinner = e.find(".sk-three-bounce").first();

    $spinner.css({
      width: "100%",
      height: "100%",
      background: "#fff",
      opacity: "0.6",
      position: "absolute",
      margin: "0",
      top: "50%",
      left: "50%",
      transform: "translate(-50%, -50%)",
      "z-index": "200",
    });

    // 3) Khóa hết tất cả các nav-link tab không cho nhấn vào khi load
    $(".nav-item").each(function () {
      $(this).css({ "pointer-events": "none", opacity: "0.5" });
    });

    // 4) Khóa hết các nút
    $(".btn, .btn-sm").each(function () {
      $(this).css({ "pointer-events": "none", opacity: "0.5" });
    });
  }
}

function enable_element(e) {
  //1)Xóa spinner đi
  $spinner = e.find(".sk-three-bounce").first();
  $spinner.remove();

  //2)Mở ra lại bình thường
  e.css({ "pointer-events": "auto", opacity: "1" });

  // 3) Mở hết tất cả các nav-link đã khóa
  $(".nav-item").each(function () {
    $(this).css({ "pointer-events": "auto", opacity: "1" });
  });

  // 4) Khóa hết các nút
  $(".btn, .btn-sm").each(function () {
    $(this).css({ "pointer-events": "auto", opacity: "1" });
  });
}
