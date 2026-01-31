$(document).ready(function () {

    let groupsTableInitialized = false;
    let usersTableInitialized = false;
    let stockTableInitialized = false;

    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        const target = $(e.target).attr("href");

        // TAB GRUPOS
        if (target === '#tab-groups' && !groupsTableInitialized) {
            if ($.fn.DataTable) {
                $('#grupos').DataTable({
                    language: {
                        url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json"
                    }
                });
                groupsTableInitialized = true;
            }
        }

        // TAB USUARIOS
        if (target === '#tab-users' && !usersTableInitialized) {
            if ($.fn.DataTable) {
                $('#usuarios-table').DataTable({
                    language: {
                        url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json"
                    }
                });
                usersTableInitialized = true;
            }
        }

        // TAB STOCK
        if (target === '#tab-stock' && !stockTableInitialized) {
            if ($.fn.DataTable) {
                $('#inventory_management').DataTable({
                    language: {
                        url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json"
                    }
                });
                stockTableInitialized = true;
            }
        }
    });

    $(document).on("click", ".btn-edit-group", function () {
        $("#edit_group_id").val($(this).data("id"));
        $("#edit_group_name").val($(this).data("name"));
        $("#modalEditGroup").modal("show");
    });

    $(document).on("click", ".btn-del-group", function () {
        $("#del_group_id").val($(this).data("id"));
        $("#modalDeleteGroup").modal("show");
    });

    // Usuarios
    $(document).on("click", ".btn-del-ug", function () {
        $("#del_ug_id").val($(this).data("id"));
        $("#modalDeleteUG").modal("show");
    });

    // Stock
    $(document).on("click", ".btn-del-stock", function () {
        $("#del_stock_id").val($(this).data("id"));
        $("#modalDeleteStock").modal("show");
    });

    // -------- GRUPOS --------
    $(document).on("click", ".btn-edit-group", function () {
        $("#edit_group_id").val($(this).data("id"));
        $("#edit_group_name").val($(this).data("name"));
        $("#modalEditGroup").modal("show");
    });

    $(document).on("click", ".btn-del-group", function () {
        $("#del_group_id").val($(this).data("id"));
        $("#modalDeleteGroup").modal("show");
    });


    // -------- USUARIOS-GRUPO --------
    $(document).on("click", ".btn-edit-ug", function () {
        $("#edit_ug_id").val($(this).data("id"));
        $("#edit_ug_user").val($(this).data("user"));
        $("#edit_ug_group").val($(this).data("group"));
        $("#modalEditUG").modal("show");
    });

    $(document).on("click", ".btn-del-ug", function () {
        $("#del_ug_id").val($(this).data("id"));
        $("#modalDeleteUG").modal("show");
    });


    // -------- STOCK --------
    $(document).on("click", ".btn-del-stock", function () {
        $("#del_stock_id").val($(this).data("id"));
        $("#modalDeleteStock").modal("show");
    });

});