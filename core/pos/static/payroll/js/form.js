var tblPayroll;

var payroll = {

    getDeductions: function (employee_id, period, period_type, callback) {

        $.ajax({
            url: pathname,
            type: "POST",
            headers: { "X-CSRFToken": csrftoken },
            data: {
                action: "get_deductions",
                employee_id: employee_id,
                period: period,
                period_type: period_type
            },
            success: function (resp) {
                callback(resp.deductions);
            },
            error: function () {
                callback(0);
            }
        });
    },


    list: function () {

        tblPayroll = $('#tblPayroll').DataTable({
            destroy: true,
            autoWidth: false,
            ajax: {
                url: pathname,
                type: 'POST',
                headers: { 'X-CSRFToken': csrftoken },
                data: { action: 'search_employees' },
                dataSrc: ""
            },

            columns: [
                { data: 'names' },

                {
                    data: 'salary',
                    render: data => '$' + parseFloat(data).toLocaleString('es-CO'),
                    className: 'text-end'
                },

                { data: null, render: () => `<input type="number" class="form-control form-control-sm days" value="15">` },

                { data: null, render: () => `<input type="number" class="form-control form-control-sm overtime" value="0">` },

                { data: null, render: () => `<input type="number" class="form-control form-control-sm others" value="0">` },

                {
                    data: null,
                    render: () => `<input type="number" class="form-control form-control-sm deductions" value="0">`
                },

                { data: null, render: () => `<span class="seguridad_social fw-bold">$0</span>` },

                {
                    data: null,
                    render: (data, type, row) =>
                        `<span class="total fw-bold">$${parseFloat(row.salary).toLocaleString('es-CO')}</span>`
                },
            ],

            columnDefs: [
                { targets: 0, width: '25%' },
                { targets: 1, width: '10%' },
                { targets: 2, width: '10%' },
                { targets: 3, width: '13%' },
                { targets: 4, width: '13%' },
                { targets: 5, width: '13%' },
                { targets: 6, width: '13%' },
                { targets: 7, width: '17%' },
            ],

            rowCallback: function (row, data) {

                let selectedPeriodType = $('#id_period_type').val();

                let now = new Date();
                let firstDay = new Date(now.getFullYear(), now.getMonth(), 1)
                    .toISOString().split('T')[0];

                /* ---------- CALCULAR DEDUCCIONES AUTOMATICAS ---------- */

                payroll.getDeductions(data.id, firstDay, selectedPeriodType, function (value) {

                    setTimeout(()=>{
                        $(row).find('.deductions').val(value);
                        calcular();
                    }, 50);
                });


                /* ---------- CALCULO GENERAL ---------- */

                function calcular() {

                    let salary = parseFloat(data.salary) || 0;
                    let base_salary = parseFloat(data.base_salary) || 0;

                    let days = parseFloat($(row).find('.days').val()) || 0;
                    let overtime = parseFloat($(row).find('.overtime').val()) || 0;
                    let others = parseFloat($(row).find('.others').val()) || 0;
                    let deductions = parseFloat($(row).find('.deductions').val()) || 0;

                    let base = (base_salary / 30) * days;
                    let base_neto = (salary / 30) * days;

                    let seguridad_social = 0;

                    if (data.social_security) {
                        let eps = base * 0.04;
                        let afp = base * 0.04;
                        let arl = base * 0.00522;
                        seguridad_social = eps + afp + arl;
                    }

                    let total = (base_neto + overtime + others) - (deductions + seguridad_social);

                    seguridad_social = Math.round(seguridad_social);
                    total = Math.round(total);

                    $(row).find('.seguridad_social').text(
                        '$' + seguridad_social.toLocaleString('es-CO')
                    );

                    $(row).find('.total').text(
                        '$' + total.toLocaleString('es-CO')
                    );
                }


                /* ---------- EVENTOS INPUT ---------- */

                $(row).find('input').off('input').on('input', calcular);

                calcular();
            }
        });
    },


    saveAll: function () {

        var payrolls = [];

        $('#tblPayroll tbody tr').each(function () {

            let now = new Date();
            let firstDay = new Date(now.getFullYear(), now.getMonth(), 1)
                .toISOString().split('T')[0];

            let selectedPeriodType = $('#id_period_type').val();
            var row = tblPayroll.row(this).data();

            payrolls.push({
                employee_id: row.id,
                period: firstDay,
                period_type: selectedPeriodType,
                days_worked: $(this).find('.days').val(),
                overtime_hours_value: $(this).find('.overtime').val(),
                other_earnings: $(this).find('.others').val(),
                deductions: $(this).find('.deductions').val(),
            });
        });


        $.ajax({
            url: pathname,
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                action: 'save_payroll',
                payrolls: JSON.stringify(payrolls)
            },

            success: function (response) {

                if (response.success) {

                    Swal.fire({
                        title: "Nómina generada",
                        text: "La nómina se generó correctamente.",
                        icon: "success",
                        confirmButtonText: "Aceptar"
                    }).then(() => window.location.href = list_url);

                } else {
                    toastr.error(response.error);
                }
            },

            error: function (xhr) {
                toastr.error('Error al guardar: ' + xhr.responseText);
            }
        });
    }
};



$(function () {

    payroll.list();

    $('#btnSaveAll').on('click', payroll.saveAll);

    $('.select2').select2({
        language: 'es',
        theme: 'bootstrap4'
    });

});