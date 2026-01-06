var input_date_range;

function loadChart(all = false) {

    let params = {
        action: 'search_report',
        start_date: input_date_range.data('daterangepicker').startDate.format('YYYY-MM-DD'),
        end_date: input_date_range.data('daterangepicker').endDate.format('YYYY-MM-DD')
    };

    if (all) {
        params.start_date = '';
        params.end_date = '';
    }

    $.ajax({
        url: pathname,
        type: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        data: params,
        success: function (response) {

            Highcharts.chart('container', {
                chart: {
                    type: 'bar'
                },
                title: {
                    text: 'Cantidad vendida por producto'
                },
                xAxis: {
                    categories: response.categories,
                    title: {
                        text: null
                    }
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: 'Cantidad',
                        align: 'high'
                    }
                },
                tooltip: {
                    valueSuffix: ' unidades'
                },
                plotOptions: {
                    bar: {
                        dataLabels: {
                            enabled: true
                        }
                    }
                },
                credits: {
                    enabled: false
                },
                series: [{
                    name: 'Cantidad vendida',
                    data: response.data,
                    colorByPoint: true
                }]
            });
        }
    });
}

$(function () {

    input_date_range = $('input[name="date_range"]');

    input_date_range.daterangepicker({
        autoApply: true,
        locale: {format: 'YYYY-MM-DD'}
    }).on('apply.daterangepicker', function () {
        loadChart(false);
    });

    $('.btnSearchAll').on('click', function () {
        loadChart(true);
    });

    loadChart(false);
});
