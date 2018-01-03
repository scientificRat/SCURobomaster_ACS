"use strict";
var visitor_stat_tab = $("#visitor-stat");
var raw_data_tab = $("#raw-data");
var visitor_data_tab = $("#visitor-data");

var inside_visitor_table = $("#inside-visitor-table");
var visitor_stat_table = $("#visitor-stat-table");
var raw_data_table = $("#raw-data-table");
var visitor_table = $("#visitor-table");


var polling_functions = [];

var hardware_update_time = -1;
var inside_visitor_table_time = 0;
var visitor_stat_table_time = 0;
var raw_data_table_time = 0;

var visitor_stat_table_max_count = 20;

$(document).ready(function () {
    switchVisitorStat();
    $("#change-password-button").click(function () {
        var old_psw = prompt("请输入旧密码", "");
        console.log(old_psw);
        if (old_psw === null) {
            alert("操作失败");
            return;
        }
        var new_psw = prompt("请输入新密码", "");
        if (new_psw === null) {
            alert("操作失败");
            return;
        }

        changePassword(old_psw, new_psw)
    });

    $("#exit-button").click(function () {
        adminLogout(function () {
            window.location.href = "/";
        });
    });

    $("#more-visitor-stat").click(function () {
        visitor_stat_table_max_count += 20;
        queryVisitorStatDataByCount(-1, visitor_stat_table_max_count, loadTableCallback(visitor_stat_table));
    });


    setInterval(function () {
        for (var k in polling_functions) {
            polling_functions[k]();
        }
        queryUpdateTime(function (rst) {
            hardware_update_time = rst.data;
        }, function () {
            console.log("query update time fail");
        });
    }, 500);
});

var updateInsideVisitors = function () {
    if (inside_visitor_table_time !== hardware_update_time) {
        queryInsideVisitors(loadTableCallback(inside_visitor_table));
        inside_visitor_table_time = hardware_update_time;
    }
};

var updateVisitorStat = function () {
    if (visitor_stat_table_time !== hardware_update_time) {
        queryVisitorStatDataByCount(-1, visitor_stat_table_max_count, loadTableCallback(visitor_stat_table));
        visitor_stat_table_time = hardware_update_time;
    }
};

var updateRawData = function () {
    if (raw_data_table_time !== hardware_update_time) {
        queryRawData(-1, 100, loadTableCallback(raw_data_table));
        raw_data_table_time = hardware_update_time;
    }
};

function switchVisitorStat() {
    visitor_stat_tab.css("display", "block");
    raw_data_tab.css("display", "none");
    visitor_data_tab.css("display", "none");
    updateVisitorStat();
    updateInsideVisitors();
    polling_functions = [];
    polling_functions.push(updateInsideVisitors);
    polling_functions.push(updateVisitorStat);
}

function switchRawData() {
    visitor_stat_tab.css("display", "none");
    raw_data_tab.css("display", "block");
    visitor_data_tab.css("display", "none");
    updateRawData();
    polling_functions = [];
    polling_functions.push(updateRawData);
}


function switchVisitorData() {
    visitor_stat_tab.css("display", "none");
    raw_data_tab.css("display", "none");
    visitor_data_tab.css("display", "block");
    queryVisitorData(loadTableCallback(visitor_table, undefined, false, function (r) {
        console.log(r);
        deleteRegisterVisior(r[0]);
    }));
}


function loadTableCallback(table, null_html, append, delete_callback) {
    append = append || false;
    null_html = null_html || "<span style='color: #8B0000;'>unknown</span>";

    function load(rst) {
        var data = rst.data;
        if (!rst.success || data === undefined) {
            alert(rst.message + " server error!! This may be a bug");
            window.location.href = "/";
            return
        }
        if (!append) table.html("");
        for (var r in data) {
            var table_row = $("<tr></tr>");
            for (var c in data[r]) {
                var item = data[r][c];
                if (item === null) {
                    item = null_html;
                }
                table_row.append("<td>" + item + "</td>");
            }
            if (delete_callback) {
                var temp = $("<td></td>");
                table_row.append(temp);
                var button = $("<button data-card-id='' class='am-btn am-btn-sm am-btn-danger'>删除</button>");
                button.click(function () {
                    delete_callback(data[r]);
                });
                temp.append(button);
            }
            table.append(table_row);
        }
    }

    return load;
}


function ajax(type, url, data, on_success, on_fail) {
    on_success = on_success || function (rst) {
        alert("操作成功");
    };
    on_fail = on_fail || function (rst) {
        alert("操作失败： " + rst.message);
        if (rst.message === "admin login required") {
            window.location.href = "/";
        }
    };
    $.ajax({
        type: type,
        url: url,
        data: data,
        success: function (rst) {
            if (rst.success) {
                on_success(rst)
            } else {
                on_fail(rst);
            }
        },
        error: function () {
            alert("network connection fail...");
        }
    })
}

// function download(text, name, type) {
//   var a = document.getElementById("a");
//   var file = new Blob([text], {type: type});
//   a.href = URL.createObjectURL(file);
//   a.download = name;
// }

function adminLogout(on_success) {
    ajax("POST", "/admin/logout", null, on_success);
}

function changePassword(old_psw, new_psw, on_success, on_fail) {
    ajax("POST", "/admin/change-password", {old_psw: old_psw, new_psw: new_psw}, on_success, on_fail);
}


function queryInsideVisitors(on_success, on_fail) {
    ajax("GET", "/data/inside-visitor/all", null, on_success, on_fail);
}

function queryVisitorStatDataByCount(last_id, count, on_success, on_fail) {
    ajax("GET", "/data/visitor-stat/by-count", {last_id: last_id, count: count}, on_success, on_fail);
}

function queryVisitorStatDataByDate(start, end, on_success, on_fail) {
    ajax("GET", "/data/visitor-stat/by-date", {start: start, end: end}, on_success, on_fail);
}

function queryRawData(last_id, count, on_success, on_fail) {
    ajax("GET", "/data/raw/by-count", {last_id: last_id, count: count}, on_success, on_fail);
}

function queryVisitorData(on_success, on_fail) {
    ajax("GET", "/data/register-visitor/all", null, on_success, on_fail);
}

function addRegisterVisior(card_id, name, on_success, on_fail) {
    ajax("POST", "/add/register-visitor", {card_id: card_id, name: name}, on_success, on_fail);
}

function deleteRegisterVisior(id, on_success, on_fail) {
    ajax("POST", "/delete/register-visitor", {id: id}, on_success, on_fail);
}

function queryCurrentCardID(on_success, on_fail) {
    ajax("GET", "/hardware/current-card-id", null, on_success, on_fail);
}

function queryUpdateTime(on_success, on_fail) {
    ajax("GET", "/hardware/last-update-time", null, on_success, on_fail);
}

function setImportingMode(on_success, on_fail) {
    ajax("POST", "/hardware/set-mode/importing", null, on_success, on_fail);
}