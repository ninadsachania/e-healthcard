$(function () {
    /* Enable popus */
    $('[data-toggle="popover"]').popover()

    /* /admin */
    const buttons = $('#doctors button');
    $.each(buttons, (index, value) => {
        console.log(value.id);
        value.onclick = function (e) {
            $.ajax({
                url: '/admin/verify',
                data: JSON.stringify({
                    id: this.id,
                }),
                type: 'POST',
                contentType: "application/json",
                dataType: "json",
                success: data => {
                    console.log(data);
                    $('#status-' + this.id).html(data['account_state']);
                    const msg = $('#message');
                    msg.html(data['message']);
                    $('.toast').toast('show');
                }
            });
        }
    });
})