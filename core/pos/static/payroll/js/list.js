var payroll = {
    list: function () {
        $('#data').DataTable({
            autoWidth: false,
            destroy: true,
            deferRender: true,
            ajax: {
                url: pathname,
                type: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {
                    'action': 'search'
                },
                dataSrc: ""
            },
            columns: [
                { data: 'period' },
                { data: 'period_type_display' },
                { data: 'total_employees' },
                { data: 'total_earned', render: data => `$${parseFloat(data).toLocaleString()}` },
                { data: 'total_payable', render: data => `$${parseFloat(data).toLocaleString()}` },
                {
                    data: null,
                    className: "text-center",
                    render: function (data) {
                        // link con parámetros de periodo y tipo de quincena
                        return `
                            <a href="/pos/payroll/view/${data.period}/${data.period_type}/" class="btn btn-info btn-sm">
                                <i class="fas fa-eye"></i> Ver
                            </a>
                        `;
                    }
                }
            ],
            
            rowCallback: function (row, data, index) {

            },
            initComplete: function (settings, json) {
                enable_tooltip();
            }
        });
        $('#data thead th').css('background-color', '#ffffff');
    }
};

$(function () {
    payroll.list();
});