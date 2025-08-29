var tblSale;
var input_date_range;

var sale = {
    list: function (all) {
        var parameters = {
            'action': 'search',
            'start_date': input_date_range.data('daterangepicker').startDate.format('YYYY-MM-DD'),
            'end_date': input_date_range.data('daterangepicker').endDate.format('YYYY-MM-DD'),
        };
        if (all) {
            parameters['start_date'] = '';
            parameters['end_date'] = '';
        }
        tblSale = $('#data').DataTable({
            autoWidth: false,
            destroy: true,
            deferRender: true,
            ajax: {
                url: pathname,
                type: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: parameters,
                dataSrc: ""
            },
            order: [[0, 'desc']],
            columns: [
                {data: "id"},
                {data: "client.names"},
                {data: "employee.names"},
                {data: "date_joined"},
                {data: "total_dscto"},
                {data: "total"},    
                {data: "paymentmethod.name"},
                {data: "transfermethods.name"},
                {data: "service_type.name"},
                {data: "id"},
            ],
            columnDefs: [
                {
                    targets: [-5, -6],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return '$' + parseFloat(data).toLocaleString('es-CL');
                    }
                },
                {
                    targets: [-2, -3, -7],
                    class: 'text-center',
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    render: function (data, type, row) {
                        var buttons = '<a rel="detail" data-bs-toggle="tooltip" title="Detalle" class="btn btn-success btn-sm rounded-pill"><i class="fas fa-boxes"></i></a> ';
                        buttons += '<a href="' + pathname + 'delete/' + row.id + '/" data-bs-toggle="tooltip" title="Eliminar" class="btn btn-danger btn-sm rounded-pill"><i class="fas fa-trash"></i></a> ';
                        buttons += '<a href="' + pathname + 'print/invoice/' + row.id + '/" target="_blank" data-bs-toggle="tooltip" title="Imprimir" class="btn btn-secondary btn-sm rounded-pill"><i class="fas fa-print"></i></a>';
                        

                        if (row.service_type && row.service_type.id === 'delivery') {
                            buttons += '<a href="#" rel="myModalEdit" data-id="' + row.id + '" data-bs-toggle="tooltip" title="Editar Domicilio" class="btn btn-warning btn-sm rounded-pill"><i class="fas fa-edit"></i></a>';
                        }

                        return buttons;
                    }
                },
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
    input_date_range = $('input[name="date_range"]');

    $('#data tbody')
        .off()
        .on('click', 'a[rel="detail"]', function () {
            $('.tooltip').remove();
            var tr = tblSale.cell($(this).closest('td, li')).index();
            var row = tblSale.row(tr.row).data();
            $('#tblProducts').DataTable({
                autoWidth: false,
                destroy: true,
                ajax: {
                    url: pathname,
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    data: {
                        'action': 'search_detail_products',
                        'id': row.id
                    },
                    dataSrc: ""
                },
                columns: [
                    {data: "product.short_name"},
                    {data: "price_with_vat"},
                    {data: "cant"},
                    {data: "subtotal"},
                    {data: "total_dscto"},
                    {data: "total"},
                ],
                columnDefs: [
                    {
                        targets: [-1, -2, -3, -5],
                        class: 'text-center',
                        render: function (data, type, row) {
                            return '$' + parseFloat(data).toLocaleString('es-CL');
                        }
                    },
                    {
                        targets: [-4],
                        class: 'text-center',
                        render: function (data, type, row) {
                            return data;
                        }
                    }
                ],
                initComplete: function (settings, json) {

                }
            });
            $('#myModalDetail').modal('show');
        })
        .on('click', 'a[rel="update"]', function () {
            $('.tooltip').remove();
            var tr = tblSale.cell($(this).closest('td, li')).index();
            var row = tblSale.row(tr.row).data();
            window.location.href = pathname + 'update/' + row.id + '/';
        })
        .on('click', 'a[rel="myModalEdit"]', function () {
            $('.tooltip').remove();
            var tr = tblSale.cell($(this).closest('td, li')).index();
            var row = tblSale.row(tr.row).data();

            fetch( '/pos/sale/admin/get_sale/' + row.id + '/', {  // Endpoint para obtener datos de la venta
                method: 'GET',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
            })
            .then(response => response.json())
            .then(data => {
                // Llenar métodos de pago
                $('#paymentmethod').empty();
                data.paymentmethods.forEach(pm => {
                    $('#paymentmethod').append(`<option value="${pm.id}" ${pm.id == data.sale.paymentmethod ? 'selected' : ''}>${pm.name}</option>`);
                });

                // Llenar métodos de transferencia
                $('#transfermethods').empty();
                data.transfermethods.forEach(tm => {
                    $('#transfermethods').append(`<option value="${tm.id}" ${tm.id == data.sale.transfermethods ? 'selected' : ''}>${tm.name}</option>`);
                });

                $('#total').val(data.sale.total);
                $('#cash').val(data.sale.cash);
                $('#change').val(data.sale.change);
            });

            $('#myModalEdit').modal('show');

            // Guardar cambios
            $('#btnSaveEdit').off('click').on('click', function () {
                var payload = {
                    paymentmethod: $('#paymentmethod').val(),
                    transfermethods: $('#transfermethods').val(),
                    cash: parseFloat($('#cash').val()),
                };

                fetch(pathname + 'update_sale/' + row.id + '/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken,
                    },
                    body: JSON.stringify(payload),
                })
                .then(response => response.json())
                .then(resp => {
                    if (resp.success) {
                        $('#myModalEdit').modal('hide');
                        sale.list(false); // recargar tabla
                    } else {
                        alert('Error al actualizar la venta');
                    }
                });
            });
        });

    input_date_range
        .daterangepicker({
                language: 'auto',
                startDate: new Date(),
                locale: {
                    format: 'YYYY-MM-DD',
                },
                autoApply: true,
            }
        )
        .on('change.daterangepicker apply.daterangepicker', function (ev, picker) {
            sale.list(false);
        });

    $('.drp-buttons').hide();

    sale.list(false);

    $('.btnSearchAll').on('click', function () {
        sale.list(true);
    });

    $('#data tbody').on('change', '.delivered-switch', function () {
        const saleId = $(this).data('id');
        const isChecked = $(this).is(':checked');

        fetch(pathname + 'delivered/' + saleId + '/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            }
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                alert('Error al actualizar el estado de entrega.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

});