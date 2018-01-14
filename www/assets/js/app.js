"use strict";
var visitor_stat_tab = $("#visitor-stat");
var raw_data_tab = $("#raw-data");
var visitor_data_tab = $("#visitor-data");

var inside_visitor_table = $("#inside-visitor-table");
var visitor_stat_table = $("#visitor-stat-table");
var raw_data_table = $("#raw-data-table");
var visitor_table = $("#visitor-table");

var visitor_stat_exporting_panel = $("#visitor-stat-exporting-panel");
var modal_loading = $("#modal-loading");

var hardware_update_time = -1;
var on_time_update_listeners = [];
var visitor_stat_table_max_count = 20;

$(document).ready(function () {
    switchVisitorStat();
    $("#change-password-button").click(function () {
        var old_psw = prompt("请输入旧密码", "");
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
        updateVisitorStat();
    });

    $("#visitor-stat-exporting-panel-button").click(function () {
        visitor_stat_exporting_panel.toggle();
    });

    $('#my-start').datepicker().on('changeDate.datepicker.amui', function (event) {
        $('#my-startDate').text($('#my-start').data('date'));
        $(this).datepicker('close');
    });

    $('#my-end').datepicker().on('changeDate.datepicker.amui', function (event) {
        $('#my-endDate').text($('#my-end').data('date'));
        $(this).datepicker('close');
    });

    $("#visitor-stat-exporting-button").click(function () {
        queryVisitorStatDataByDate($('#my-startDate').text(), $('#my-endDate').text(), function (rst) {
            var raw = rst.data;
            var out = "卡号,姓名,学号,学院,备注,进入时间,离开时间\n";
            for (var i in raw) {
                raw[i][0] = "ID" + raw[i][0];
                out += raw[i] + "\n";
            }
            var blob = new Blob([out], {type: "text/csv;charset=utf-8"});
            var date = new Date();
            var filename = "visitors-stat-" + date.toLocaleDateString().replace(/\//g, "-") + ".csv";
            saveAs(blob, filename);
        });
    });

    $("#add-register-visitor-button").click(function () {
        var row = $("<tr></tr>");
        row.append("<td>--</td>");

        var td_card_id = $("<td></td>");
        var card_id_input_group = $("<div class='am-input-group'></div>");
        td_card_id.append(card_id_input_group);
        var td_name = $("<td></td>");
        var td_student_id = $("<td></td>");
        var td_college = $("<td></td>");
        var td_remark = $("<td></td>");
        var td_operation = $("<td style='width: 16%'></td>");

        var card_id_input = $("<input class='am-form-field' type='text' placeholder='卡号'>");
        var read_from_hardware_button = $("<span class='am-input-group-btn'><button class='am-btn am-btn-default'>从设备读取</button></span>");
        var name_input = $("<input class='am-form-field' type='text' placeholder='姓名'>");
        var student_id_input = $("<input class='am-form-field' type='text' placeholder='学号'>");
        var college_input = $("<input class='am-form-field' type='text' placeholder='学院'>");
        var remark_input = $("<input class='am-form-field' type='text' placeholder='备注'>");
        var cancel_button = $("<button class='am-btn am-btn-danger am-btn-sm'>取消</button>");
        var save_button = $("<button class='am-btn am-btn-primary am-btn-sm'>保存</button>");

        card_id_input_group.append(card_id_input, read_from_hardware_button);
        td_name.append(name_input);
        td_student_id.append(student_id_input);
        td_college.append(college_input);
        td_remark.append(remark_input);
        td_operation.append(cancel_button, "<span> </span>", save_button);
        row.append(td_card_id, td_name, td_student_id, td_college, td_remark, td_operation);
        visitor_table.append(row);

        read_from_hardware_button.click(function () {
            modal_loading.modal();
            setImportingMode(function () {
                var on_update = function () {
                    queryCurrentCardID(function (rst) {
                        card_id_input.val(rst.data);
                        modal_loading.modal('close');
                        on_time_update_listeners = []
                    }, function (rst) {
                        alert(rst.message + " error ");
                        modal_loading.modal('close');
                        on_time_update_listeners = []
                    });
                };
                on_time_update_listeners.push(on_update);
            });
        });

        cancel_button.click(function () {
            row.detach();
        });

        save_button.click(function () {
            var card_id = card_id_input.val();
            var name = name_input.val();
            var student_id = student_id_input.val();
            var college = college_input.val();
            var remark = remark_input.val();
            if (card_id === "" || name === "") {
                alert("卡号, 姓名 不能为空");
            } else {
                addRegisterVisitor(card_id, name, student_id, college, remark, updateVisitors);
            }
        });
    });

    setInterval(function () {
        queryUpdateTime(function (rst) {
            var curr_time = rst.data;
            if (curr_time !== hardware_update_time) {
                for (var k in on_time_update_listeners) {
                    on_time_update_listeners[k]();
                }
                hardware_update_time = curr_time;
            }
        }, function () {
            console.log("query update time fail");
        });
    }, 500);
});

var updateInsideVisitors = function () {
    queryInsideVisitors(loadTableCallback(inside_visitor_table));
};

var updateVisitorStat = function () {
    queryVisitorStatDataByCount(-1, visitor_stat_table_max_count, loadTableCallback(visitor_stat_table, undefined, false, function (r) {
        if (confirm("确认删除记录 ?")) {
            deleteVisitorStat(r[0], updateVisitorStat);
        }
    }, [0]));
};

var updateRawData = function () {
    queryRawData(-1, 100, loadTableCallback(raw_data_table));
};

var updateVisitors = function () {
    queryVisitorData(loadTableCallback(visitor_table, undefined, false, function (r) {
        if (confirm("确认删除 " + r[2] + " ?")) {
            deleteRegisterVisitor(r[0], updateVisitors);
        }
    }));
};


function switchVisitorStat() {
    visitor_stat_tab.fadeIn();
    raw_data_tab.hide();
    visitor_data_tab.hide();
    updateVisitorStat();
    updateInsideVisitors();
    on_time_update_listeners = [];
    on_time_update_listeners.push(updateInsideVisitors);
    on_time_update_listeners.push(updateVisitorStat);
}

function switchRawData() {
    raw_data_tab.fadeIn();
    visitor_stat_tab.hide();
    visitor_data_tab.hide();
    updateRawData();
    on_time_update_listeners = [];
    on_time_update_listeners.push(updateRawData);
}

function switchVisitorData() {
    visitor_data_tab.fadeIn();
    visitor_stat_tab.hide();
    raw_data_tab.hide();
    on_time_update_listeners = [];
    updateVisitors();
}

function loadTableCallback(table, null_html, append, delete_callback, no_display_cols) {
    append = append || false;
    null_html = null_html || "<span style='color: #8B0000;'>N/A</span>";
    no_display_cols = no_display_cols || [];
    var load = function (rst) {
        var data = rst.data;
        if (!rst.success || data === undefined) {
            alert(rst.message + " server error!! This may be a bug");
            window.location.href = "/";
            return;
        }
        if (!append) table.html("");
        for (var r in data) {
            var table_row = $("<tr></tr>");
            for (var c in data[r]) {
                if (c in no_display_cols) {
                    continue;
                }
                var item = data[r][c];
                if (item === null) {
                    item = null_html;
                }
                table_row.append("<td>" + item + "</td>");
            }
            if (delete_callback) {
                var delete_d = $("<td></td>");
                table_row.append(delete_d);
                var button = $("<button class='am-btn am-btn-sm am-btn-danger'>删除</button>");
                (function (t) {
                    button.click(function () {
                        delete_callback(t);
                    });
                })(data[r]);

                delete_d.append(button);
            }
            table.append(table_row);
        }
    };

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

function deleteVisitorStat(id, on_success, on_fail) {
    ajax("POST", "/delete/visitor-stat/by-id", {id: id}, on_success, on_fail)
}

function queryRawData(last_id, count, on_success, on_fail) {
    ajax("GET", "/data/raw/by-count", {last_id: last_id, count: count}, on_success, on_fail);
}

function queryVisitorData(on_success, on_fail) {
    ajax("GET", "/data/register-visitor/all", null, on_success, on_fail);
}

function addRegisterVisitor(card_id, name, student_id, college, remark, on_success, on_fail) {
    ajax("POST", "/add/register-visitor", {
        card_id: card_id,
        name: name,
        student_id: student_id,
        college: college,
        remark: remark
    }, on_success, on_fail);
}

function deleteRegisterVisitor(id, on_success, on_fail) {
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