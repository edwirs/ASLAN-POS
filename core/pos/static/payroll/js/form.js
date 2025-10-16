var tblPayroll;
var input_period_type;

var payroll = {
    list: function () {
        tblPayroll = $('#tblPayroll').DataTable({
            destroy: true,
            autoWidth: false,
            ajax: {
                url: pathname,
                type: 'POST',
                headers: { 'X-CSRFToken': csrftoken },
                data: { 'action': 'search_employees' },
                dataSrc: ""
            },
            columns: [
                { data: 'names' },
                {
                    data: 'salary',
                    render: function (data) {
                        return '$' + parseFloat(data).toLocaleString('es-CO');
                    },
                    className: 'text-end'
                },
                {
                    data: null,
                    render: function () {
                        return `<input type="number" class="form-control form-control-sm days" value="15">`;
                    }
                },
                {
                    data: null,
                    render: function () {
                        return `<input type="number" class="form-control form-control-sm overtime" value="0">`;
                    }
                },
                {
                    data: null,
                    render: function () {
                        return `<input type="number" class="form-control form-control-sm others" value="0">`;
                    }
                },
                {
                    data: null,
                    render: function () {
                        return `<input type="number" class="form-control form-control-sm deductions" value="0">`;
                    }
                },
                {
                    data: null,
                    render: function () {
                        return `<span class="seguridad_social text-end fw-bold">$0</span>`;
                    },
                },
                {
                    data: null,
                    render: function (data, type, row) {
                        return `<span class="total text-end fw-bold">$${parseFloat(row.salary).toLocaleString('es-CO')}</span>`;
                    }
                },
            ],
            columnDefs: [
                { targets: 0, width: '25%' },  // Empleado
                { targets: 1, width: '10%' },  // Salario
                { targets: 2, width: '10%' },  // Días
                { targets: 3, width: '13%' },  // Horas extra
                { targets: 4, width: '13%' },  // Otros ingresos
                { targets: 5, width: '13%' },  // Deducciones
                { targets: 6, width: '13%' },  // seguridad social
                { targets: 7, width: '17%' },  // Total estimado
            ],
            rowCallback: function (row, data) {
                // Recalcular totales cuando cambien valores
                function calcular() {
                    let salary = parseFloat(data.salary) || 0;
                    let base_salary = parseFloat(data.base_salary) || 0;
                    let days = parseFloat($(row).find('.days').val()) || 0;
                    let overtime = parseFloat($(row).find('.overtime').val()) || 0;
                    let others = parseFloat($(row).find('.others').val()) || 0;
                    let deductions = parseFloat($(row).find('.deductions').val()) || 0;

                    // 🔹 Proporcional del salario por días trabajados
                    let base = (base_salary / 30) * days;
                    let base_neto = (salary / 30) * days;

                    // 🔹 Aportes calculados sobre el salario base quincenal
                    // se calcula la eps en base al minimo por acuerdo con empleados
                    let seguridad_social = 0;
                    console.log(data);
                    if (data.social_security) {
                        let eps = base * 0.04;     // 4%
                        let afp = base * 0.04;     // 4%
                        let arl = base * 0.00522;  // 0.522%
                        seguridad_social = eps + afp + arl;
                    }

                    // 🔹 Total neto quincenal
                    let total = (base_neto + overtime + others) - (deductions + seguridad_social);

                    seguridad_social = Math.round(seguridad_social);
                    total = Math.round(total);
                    
                    // Mostrar valores
                    $(row).find('.seguridad_social').text(
                        '$' + seguridad_social.toLocaleString('es-CO', { minimumFractionDigits: 0 })
                    );
                    $(row).find('.total').text(
                        '$' + total.toLocaleString('es-CO', { minimumFractionDigits: 0 })
                    );
                }

                // Vincula el cálculo a los cambios
                $(row).find('input').off('input').on('input', calcular);

                // ⚡ Calcula automáticamente al cargar la fila
                calcular();
            }
        });
    },

    saveAll: function () {
        var payrolls = [];
        $('#tblPayroll tbody tr').each(function () {
            let now = new Date();
            let firstDay = new Date(now.getFullYear(), now.getMonth(), 1)
                .toISOString()
                .split('T')[0];
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
                'action': 'save_payroll',
                'payrolls': JSON.stringify(payrolls)
            },
            success: function (response) {
                if (response.success) {
                    Swal.fire({
                        title: "Nómina generada",
                        text: "La nómina se generó correctamente.",
                        icon: "success",
                        confirmButtonText: "Aceptar"
                    }).then(() => {
                        // Redirige al listado principal
                        window.location.href = list_url;
                    });
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

    $('#btnSaveAll').on('click', function () {
        payroll.saveAll();
    });

    $('.select2').select2({
        language: 'es',
        theme: 'bootstrap4'
    });
});