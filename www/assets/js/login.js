"use strict";

$("#submit").click(function () {
    var username = $("#username").val();
    var password = $("#password").val();
    if(username==="" || password ===""){
        alert("不能为空");
        return;
    }
    $.post("/admin/login", {username: username, password: password}, function (rst) {
        if (rst.success) {
            window.location.href = "/main.html"
        } else {
            alert("登录失败" + rst.message);
        }
    })
});