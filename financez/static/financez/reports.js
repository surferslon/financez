var create_report = function(response) {
    var expenses_accs
    var incomes_accs
    var seriesSource = []
    var dataSource = [{}]
    var ExpIndes = response.accounts_incomes.length

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
            columnCount: 2,
            customizeItems: function(items) {
                var sortedItems = [];
                items.forEach(function (item) {
                    var startIndex = item.series.stack === "incomes" ? 0 : ExpIndes;
                    sortedItems.splice(startIndex, 0, item);
                });
                return sortedItems;
            }
        },
        valueAxis: {
        },
        loadingIndicator: {
            enabled: true
        },
        "export": {
            enabled: false
        },
        onPointClick: function (e) {
            e.target.select();
        },
        tooltip: {
            enabled: true,
            customizeTooltip: function (arg) {
                return { text: arg.seriesName + "\n" + parseFloat(arg.valueText).toFixed(3) }
            },
        }
    });
}

$(function() {
    let data_url = $('.demo-container').data('url')
    $.get(data_url, create_report );
    $('#update-report').click(function(event){
        $.get([data_url, '?period-from=', $('#period-from').val(), '&period-to=', $('#period-to').val()].join(''), create_report );
    })
});

