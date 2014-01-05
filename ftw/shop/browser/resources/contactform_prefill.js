jQuery(function ($) {
    // Load contact info depending on personnel no.
    $('input#contact_information-widgets-personnel_no').blur(function (event) {
        // Do something here
    });


    // Grey-out address field unless "Different from invoice address" is checked
    $('input#shipping_address-widgets-used-0').click(function (event) {
        var state = !($(this).attr('checked'));
        toggle_fields(state);
    });

    var toggle_fields = function (state) {
        var fields = $('#wizard-step-shipping_address input')
                     .not('input#shipping_address-widgets-used-0')
                     .not('.submit-widget');
        fields.each(function () {
            $(this).attr("readonly", state);
            if (state == true) {
                $(this).addClass("greyed-out");
            }
            else {
                $(this).removeClass("greyed-out");
            }
        });
    };

    // Set initial state of fields on page load
    toggle_fields(!($('input#shipping_address-widgets-used-0').attr('checked')));

});
