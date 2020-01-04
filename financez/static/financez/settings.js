$('.acc-tree-item').change(function(event){
    let elem = $(event.target)
    let acc_pk = elem.parent().data('accpk')
    let acc_field = elem.data('field')
    $.ajax({
        type: "POST",
        url: $('#acc-list').data('url'),
        data: {
            acc_pk: acc_pk,
            acc_field: acc_field,
            value: elem.val(),
            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value
        },
        success: function(resp){
            if (['parent', 'results'].includes(acc_field)) {
                window.location.reload(true);
            }

        },
    })
})