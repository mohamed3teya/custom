//sidebar toggle button menu



//when click  sidebar toggle button
$(".sidebar-toggle").on("click", function (e) {
  localStorage.setItem("menu", !$("body").hasClass("sidebar-collapse"));
  $("#logo-large").toggle();
});

// check status sidebar toggle  from localStorage
$("document").ready(function () {
  var state = localStorage.getItem("menu");

  if (state === null) {
    $("body").removeClass("sidebar-collapse");
    $("#logo-large").show();

  } else {
    var closed = state === "true" ? true : false;

    if (closed) {
      $("body").addClass("sidebar-collapse");
      $("#logo-large").hide();
      
       
    } else {
      $("body").removeClass("sidebar-collapse");
    }
  }
});
