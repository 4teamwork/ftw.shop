jq(function() {

    // Hide Enabled Payment Processor selection if NoPaymentProcessorStepGroup selected
    jq("select#form-widgets-payment_processor_step_group").change(function () {

        if (jq("select#form-widgets-payment_processor_step_group option:selected").attr("value") == "ftw.shop.NoPaymentProcessorStepGroup") {
            // hide
     	   jq("#formfield-form-widgets-enabled_payment_processors").hide();
        }
        else {
            // show
     	   jq("#formfield-form-widgets-enabled_payment_processors").show();
        }
   }).change();
  
});

     


     
     