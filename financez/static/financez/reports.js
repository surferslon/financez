var show_entries = function(response) {
    $('#report_entries').css('display', 'flex');
    $('#report_entries').html(response);
}

var create_report = function(response) {
    var expenses_accs
    var incomes_accs
    var seriesSource = []
    var dataSource = [{}]
    var ExpIndex = response.accounts_incomes.length

    for (var i=0; i<response.accounts_incomes.length; i++) {
        seriesSource.push({
            valueField: response.accounts_incomes[i],
            name: response.accounts_incomes[i],
            stack: 'incomes',
        })
    }
    for (var i=0; i<response.accounts_expenses.length; i++) {
        seriesSource.push({
            valueField: response.accounts_expenses[i],
            name: response.accounts_expenses[i],
            stack: 'expenses',
        })
    }

    $("#chart").dxChart({
        palette: "Soft Pastel",
        dataSource: response.results,
        commonSeriesSettings: {
            argumentField: "group_date",
            type: "stackedBar",
            hoverMode: "allSeriesPoints",
            selectionMode: "allSeriesPoints",
        },
        series: seriesSource,
        legend: {
            horizontalAlignment: "left",
            verticalAlignment: "top",
            position: "outside",
            border: { visible: false },
            columnCount: 1,
        },
        valueAxis: { },
        loadingIndicator: { enabled: true },
        "export": { enabled: false },
        onSeriesClick: function(e) {
            e.target.select();
            let data_details_url = $('.demo-container').data('details-url')
            $.get([
                data_details_url,
                '?category=', e.target.name,
                '&period-from=', $('#period-from').val(),
                '&period-to=', $('#period-to').val()
            ].join(''), create_report_details)
        },
        tooltip: {
            enabled: true,
            customizeTooltip: function (arg) {
                return { text: arg.seriesName + "\n" + parseFloat(arg.valueText).toFixed(3) }
            },
        }
    });
}

var create_report_details = function(response) {
    $("#chart_details").parents('.dx-viewport').removeClass('dx_hidden');
    $("#chart_details").dxChart({
        palette: "soft",
        dataSource: response.results,
        commonSeriesSettings: {
            barPadding: 0.5,
            argumentField: "group_date",
            type: "bar",
            label: {
                visible: true,
                format: {
                    type: "fixedPoint",
                    precision: 3,
                }
            }
        },
        series: response.accounts,
        legend: {
            horizontalAlignment: "left",
            verticalAlignment: "top",
        },
        onSeriesClick: function(e) {
            e.target.select();
            acc_id = e.target.getValueFields()[0]
            let report_entries_url = $('#report_entries').data('entries-url')
            $.get([
                report_entries_url ,
                '?acc_id=', acc_id,
                '&period-from=', $('#period-from').val(),
                '&period-to=', $('#period-to').val()
            ].join(''), show_entries)
        },
        title: { text: response.title, },
    });
}

$(function() {
    let data_url = $('.demo-container').data('url')
    $.get(data_url, create_report);
    $('#update-report').click(function(event){
        $.get([
            data_url,
            '?period-from=', $('#period-from').val(),
            '&period-to=', $('#period-to').val(),
            '&group_all=', $('#group_all').is(":checked")
        ].join(''), create_report );
    })
    $('#modal-background').click(function(event) {
        $('#modal-background').css('display', 'none');
        $('#report_details').css('display', 'none');
        $('body').css('overflow', 'auto');
    });
});

