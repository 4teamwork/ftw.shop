jQuery(function($) {

    // Hide Enabled Payment Processor selection if NoPaymentProcessorStepGroup selected
    $("select#form-widgets-payment_processor_step_group").change(function () {

        if ($("select#form-widgets-payment_processor_step_group option:selected").attr("value") == "ftw.shop.NoPaymentProcessorStepGroup") {
            // hide
     	   $("#formfield-form-widgets-enabled_payment_processors").hide();
        }
        else {
            // show
     	   $("#formfield-form-widgets-enabled_payment_processors").show();
        }
   }).change();

});
