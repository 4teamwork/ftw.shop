
     jq(function() {
         // Add item to cart through AJAX request
         jq('input[name=addtocart]').click(function(event) {
             event.preventDefault();

             if (jq(this).hasClass('compact')) {
                // We're in compact_view, therefor the input's positions inside 
                // the forms are different
                                
                // Get the containing form's action URL
                var url;
                url = jq(this).parent().parent().parent().attr('action');
                var var1choice = jq(this).parent().parent().find('select[name=var1choice]').find('option:selected').val();
                var var2choice = jq(this).parent().parent().find('select[name=var2choice]').find('option:selected').val();
                var itemdata;
                if (var1choice == undefined) {
                    // We don't have variations - reference the item by its skuCode
                    itemdata = {skuCode: jq(this).siblings().filter('input[name=skuCode]').val(),
                                    quantity: jq(this).siblings().filter('input[name=quantity:int]').val()};
                }
                else {
                    if (var2choice == undefined) {
                        // We've got one variation
                        itemdata = {var1choice: var1choice,
                                        quantity: jq(this).siblings().filter('input[name=quantity:int]').val()};
                    }
                    else {
                        // We've got two variations
                        itemdata = {var1choice: var1choice,
                                        var2choice: var2choice,
                                        quantity: jq(this).siblings().filter('input[name=quantity:int]').val()};
                    }
                }
             }
             else {
                // Get the containing form's action URL
                url = jq(this).parent().attr('action');
                // Get skuCode and quantity from adjacent input fields
                itemdata = {skuCode: jq(this).siblings().filter('input[name=skuCode]').val(),
                                quantity: jq(this).siblings().filter('input[name=quantity:int]').val()};
             }

             jq.getJSON(url + "_ajax", itemdata,
                 function(response) {
                     // Add item to cart, receive updated portlet html and translated status message
                     var portlet_html = response['portlet_html'];
                     var status_message = response['status_message'];
                     jq('.portletCartPortlet').replaceWith(portlet_html);
                     jq('#kssPortalMessage').html(status_message);
                     jq('#kssPortalMessage').fadeIn().delay(2000).fadeOut();
                 });
         });


            // Only show matching item variation depending on user selection
            jq("select").change(function () {
                  var varkey;
                  if (jq("select[name=var2choice]").length == 0) {
                      // We only have one variation
                      varkey = jq("select[name=var1choice] option:selected").attr("value"); 
                  }
                  else {
                      // We've got two variations
                      varkey = jq("select[name=var1choice] option:selected").attr("value") + "-" + 
                               jq("select[name=var2choice] option:selected").attr("value"); 
                  }
                      jq("table#itemDataTable tr").hide();
                      jq("table#itemDataTable tr").each( function() {
                            if (varkey == jq(this).attr("id")) {
                                jq(this).show();
                                }
                            });
             }).change();
      });