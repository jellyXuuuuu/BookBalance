$(function () {
    //$('#charts-nav').click(function () {
    $("#top-container").attr("class", "container-fluid");
    const urls = document.getElementById('urls');
    const retrieveYearHasDataURL = urls.getAttribute('data-retrieve-year-has-data-url');
    const retrieveMonthHasDataURL = urls.getAttribute('data-retrieve-month-has-data-url');
    const retrieveYearURL = urls.getAttribute('data-retrieve-current-year-income-expense-url');
    const retrieveMonthURL = urls.getAttribute('data-retrieve-current-month-income-expense-url');

    $.ajax({
        type: "GET",
        url: retrieveYearHasDataURL,
        cache: false,
        dataType: "json",
        success: function (result) {
            var options = '<option value="select value" selected="selected">Choose Year</option>';
            result["years"].forEach(function (val, index, arr) {
                new_option = '<option value="' + val + '">' + val + '</option>';
                options += new_option;
            });
            var year_list = document.getElementById("available-years");
            year_list.innerHTML = options;
            var month_options = '<option value="select value" selected="selected">Choose Month</option>';
            var month_list = document.getElementById("available-months");
            month_list.innerHTML = month_options;
        }
    });

    var monthBarChart = echarts.init(document.getElementById('month-bar-chart'));
    var monthBarOption = {
        title: {
            text: 'Daily record of the month',
            left: 'center'
        },
        grid: {
            containLabel: true,
            left: '3%',
            right: '3%',
            bottom: '4%',
            top: '13%'
        },
        legend: {
            data: ['Expenditure', 'Income'],
            x: 'right',
            y: 'bottom'
        },
        tooltip: {},
        xAxis: {
            data: [],
            axisLabel: {
                rotate: 30,
                margin: 8
            },
            splitLine: {
                show: true
            }
        },
        yAxis: {},
        series: [{
            name: 'Expenditure',
            type: 'bar',
            color: '#FF4500',
            data: [],
            animationDelay: function (idx) {
                return idx * 10;
            }
        }, {
            name: 'Income',
            type: 'bar',
            color: '#3CB371',
            data: [],
            animationDelay: function (idx) {
                return idx * 10 + 100;
            }
        }],
        animationEasing: 'elasticOut',
        animationDelayUpdate: function (idx) {
            return idx * 5;
        }
    };
    monthBarChart.setOption(monthBarOption);


    var monthPieChart = echarts.init(document.getElementById('month-pie-chart'));
    var monthPieOption = {
        title: {
            text: 'Proportion of for the month',
            subtext: 'Income | Expenditure',
            left: 'center'
        },
        tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b} : {c} ({d}%)'
        },
        grid: {
            containLabel: true,
            left: '3%',
            right: '3%',
            bottom: '4%',
            top: '13%'
        },
        legend: {
            left: 'center',
            top: 'bottom',
            show: false,
            data: []
        },
        series: [
            {
                name: 'Income',
                type: 'pie',
                radius: [30, 80],
                center: ['25%', '50%'],
                roseType: 'radius',
                label: {
                    show: true
                },
                emphasis: {
                    label: {
                        show: true
                    }
                },
                data: [],
                color: ['#2E8B57', '#3CB371', '#20B2AA', '#32CD32', '#2E8B57'],
                itemStyle: {
                    normal: {
                        label: {
                            show: true,
                            position: 'top',
                            color: '#000',
                            formatter: '{b} \n{c}',
                        }
                    }
                }
            },
            {
                name: 'Expenditure',
                type: 'pie',
                radius: [30, 80],
                center: ['75%', '50%'],
                roseType: 'area',
                data: [],
                color: ['#FF7F50', '#A0522D', '#D2691E', '#FFA07A', '#FF8C00', '#FFDAB9', '#CD5C5C', '#DAA520'],
                itemStyle: {
                    normal: {
                        label: {
                            show: true,
                            position: 'top',
                            color: '#000',
                            formatter: '{b} \n{c}',
                        }
                    }
                }
            }
        ]
    };
    monthPieChart.setOption(monthPieOption);


    var yearBarChart = echarts.init(document.getElementById('year-bar-chart'));
    var yearBarOption = {
        title: {
            text: 'Monthly records for the year',
            left: 'center'
        },
        grid: {
            containLabel: true,
            left: '3%',
            right: '3%',
            bottom: '14%',
            top: '13%'
        },
        legend: {
            data: ['Expenditure', 'Income'],
            x: 'right',
            y: 'bottom'
        },
        tooltip: {},
        xAxis: {
            data: [],
            axisLabel: {
                //interval: 3,
                //rotate: 30
            },

            splitLine: {
                show: true
            }
        },
        yAxis: {},
        series: [{
            name: 'Expenditure',
            type: 'bar',
            color: '#FF4500',
            data: [],
            animationDelay: function (idx) {
                return idx * 10;
            }
        }, {
            name: 'Income',
            type: 'bar',
            color: '#3CB371',
            data: [],
            animationDelay: function (idx) {
                return idx * 10 + 100;
            }
        }],
        animationEasing: 'elasticOut',
        animationDelayUpdate: function (idx) {
            return idx * 5;
        }
    };
    yearBarChart.setOption(yearBarOption);

    var yearPieChart = echarts.init(document.getElementById('year-pie-chart'));
    var yearPieOption = {
        title: {
            text: 'Proportion types for the year',
            subtext: 'Income | Expenditure',
            left: 'center'
        },
        tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b} : {c} ({d}%)'
        },
        legend: {
            left: 'center',
            top: 'bottom',
            show: false,
            data: []
        },
        series: [
            {
                name: 'Income',
                type: 'pie',
                radius: [30, 80],
                center: ['25%', '50%'],
                roseType: 'radius',
                label: {
                    show: true
                },
                emphasis: {
                    label: {
                        show: true
                    }
                },
                data: [],
                color: ['#2E8B57', '#3CB371', '#20B2AA', '#32CD32', '#2E8B57'],
                itemStyle: {
                    normal: {
                        label: {
                            show: true,
                            position: 'top',
                            color: '#000',
                            formatter: '{b} \n{c}',
                        }
                    }
                }
            },
            {
                name: 'Expenditure',
                type: 'pie',
                radius: [30, 80],
                center: ['75%', '50%'],
                roseType: 'area',
                data: [],
                color: ['#FF7F50', '#A0522D', '#D2691E', '#FFA07A', '#FF8C00', '#FFDAB9', '#CD5C5C', '#DAA520'],
                itemStyle: {
                    normal: {
                        label: {
                            show: true,
                            position: 'top',
                            color: '#000',
                            formatter: '{b} \n{c}',
                        }
                    }
                }
            }
        ]
    };
    yearPieChart.setOption(yearPieOption);

    $.ajax({
        type: "GET",
        url: retrieveMonthURL,
        cache: false,
        dataType: "json",
        success: function (result) {
            $("#month-total-income").text(result["month_total_income"]);
            $("#month-total-expense").text(result["month_total_expense"]);
            monthBarOption.xAxis.data = result["days"];
            monthBarOption.series[0].data = result["days_expense"];
            monthBarOption.series[1].data = result["days_income"];
            monthBarChart.setOption(monthBarOption);
            monthPieOption.legend.data = result["month_category_names"];
            monthPieOption.series[0].data = result["month_category_income"];
            monthPieOption.series[1].data = result["month_category_expense"];
            monthPieChart.setOption(monthPieOption);
        }
    });

    $.ajax({
        type: "GET",
        url: retrieveYearURL,
        cache: false,
        dataType: "json",
        success: function (result) {
            $("#year-total-income").text(result["year_total_income"]);
            $("#year-total-expense").text(result["year_total_expense"]);
            yearBarOption.xAxis.data = result["months"];
            yearBarOption.series[0].data = result["months_expense"];
            yearBarOption.series[1].data = result["months_income"];
            yearBarChart.setOption(yearBarOption);
            yearPieOption.legend.data = result["year_category_names"];
            yearPieOption.series[0].data = result["year_category_income"];
            yearPieOption.series[1].data = result["year_category_expense"];
            yearPieChart.setOption(yearPieOption);
        }
    });

    $('#available-years').change(function () {
        var current_selected_year = $(this).children('option:selected').text();
        $.ajax({
            type: "POST",
            data: {year: current_selected_year},
            url: retrieveMonthHasDataURL,
            cache: false,
            dataType: "json",
            success: function (result) {
                var options = '<option value="select value" selected="selected">Choose Month</option>';
                result["months"].forEach(function (val, index, arr) {
                    new_option = '<option value="' + val + '">' + val + '</option>';
                    options += new_option;
                });
                var month_list = document.getElementById("available-months");
                month_list.innerHTML = options;
            }
        });
    });

    $('#show-charts').click(function () {
        var selected_year = $('#available-years').children('option:selected').text();
        var selected_month = $('#available-months').children('option:selected').text();
        var re = /^[0-9]+.?[0-9]*/;
        if (re.test(selected_year) && re.test(selected_month)) {
            $.ajax({
                type: "POST",
                data: {year: selected_year, month: selected_month},
                url: retrieveMonthURL,
                cache: false,
                dataType: "json",
                success: function (result) {
                    $("#month-total-income").text(result["month_total_income"]);
                    $("#month-total-expense").text(result["month_total_expense"]);
                    monthBarOption.xAxis.data = result["days"];
                    monthBarOption.series[0].data = result["days_expense"];
                    monthBarOption.series[1].data = result["days_income"];
                    monthBarChart.setOption(monthBarOption);
                    monthPieOption.legend.data = result["month_category_names"];
                    monthPieOption.series[0].data = result["month_category_income"];
                    monthPieOption.series[1].data = result["month_category_expense"];
                    monthPieChart.setOption(monthPieOption);
                }
            });

            $.ajax({
                type: "POST",
                data: {year: selected_year},
                url: retrieveYearURL,
                cache: false,
                dataType: "json",
                success: function (result) {
                    $("#year-total-income").text(result["year_total_income"]);
                    $("#year-total-expense").text(result["year_total_expense"]);
                    yearBarOption.xAxis.data = result["months"];
                    yearBarOption.series[0].data = result["months_expense"];
                    yearBarOption.series[1].data = result["months_income"];
                    yearBarChart.setOption(yearBarOption);
                    yearPieOption.legend.data = result["year_category_names"];
                    yearPieOption.series[0].data = result["year_category_income"];
                    yearPieOption.series[1].data = result["year_category_expense"];
                    yearPieChart.setOption(yearPieOption);
                }
            });
        } else {
            alert("Please select year and month!");
        }
    });

    //});

})

$.ajaxSetup({headers: {"X-CSRFToken": '{{ csrf_token }}'}});

