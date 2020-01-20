$(function() {
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

    $('.cur-button').click(function(event){
        let cur_id = $(event.target).data('curid')
        let url = $('.currencies-list').data('url')
        $.ajax({
            type: "POST",
            url: url,
            data: {
                cur_pk: cur_id,
                csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value
            },
            success: function(resp){
                window.location.reload(true);

            },
        })
    })

    $('#new-acc-button').click(function(event) {
        $('#modal-background').css('display', 'flex');
        $('#modal-new-acc').css('display', 'block');
        $('body').css('overflow', 'hidden');
    })

    $('#add-currency-button').click(function(event) {
        event.preventDefault()
        $('#modal-background').css('display', 'flex');
        $('#modal-new-cur').css('display', 'block');
        $('body').css('overflow', 'hidden');
    })

    $('.del-button').click(function(event) {
        event.preventDefault()
        $('#modal-background').css('display', 'flex');
        $('#modal-del-acc').css('display', 'block');
        $('#form-del-acc').attr('action', event.target.href)
    })

    $('#modal-background').click(function(event) {
        $('#modal-background').css('display', 'none');
        $('#modal-new-acc').css('display', 'none');
        $('#modal-new-cur').css('display', 'none');
        $('#modal-del-acc').css('display', 'none');
        $('body').css('overflow', 'auto');
    });


})