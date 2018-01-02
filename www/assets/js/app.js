"use strict";
var visitor_stat_tab = $("#visitor-stat");
var raw_data_tab = $("#raw-data");
var visitor_data_tab = $("#visitor-data");
var polling_functions = [];

$(document).ready(function () {
    switchVisitorStat();
    setInterval(function () {
        for (var k in polling_functions) {
            polling_functions[k]();
        }

    }, 500);
});


function switchVisitorStat() {
    visitor_stat_tab.css("display", "block");
    raw_data_tab.css("display", "none");
    visitor_data_tab.css("display", "none");

}

function switchRawData() {
    visitor_stat_tab.css("display", "none");
    raw_data_tab.css("display", "block");
    visitor_data_tab.css("display", "none");
}


function switchVisitorData() {
    visitor_stat_tab.css("display", "none");
    raw_data_tab.css("display", "none");
    visitor_data_tab.css("display", "block");
}



function queryVisitorStatData(last_id,count) {
    $.ajax({
        type:"GET",
        url:"/data/visitor-stat/by-count",
        data:{last_id:last_id,count:count},
        success:function (rst) {

        },
        error:function () {
            alert("connection fail...");
        }
    })
}