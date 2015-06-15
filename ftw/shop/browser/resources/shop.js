jQuery(function ($) {
    // Add item to cart through AJAX request
    $('input[name="addtocart"]').click(function (event) {
        event.preventDefault();

        if ($(this).hasClass('compact')) {
            // We're in compact_view, therefore the input's positions inside
            // the forms are different
            // Get the containing form's action URL
            var url;
            url = $(this).parents('form').attr('action');
            var var1choice = $(this).parents('form').find('select[name="var1choice"]').find('option:selected').val();
            var var2choice = $(this).parents('form').find('select[name="var2choice"]').find('option:selected').val();
            var itemdata;
            if (var1choice == undefined) {
                // We don't have variations - reference the item by its skuCode
                itemdata = {
                    skuCode: $(this).parents('form').find('input[name="skuCode"]').val(),
                    quantity: $(this).parents('form').find('input[name="quantity:int"]').val()
                };
            }
            else {
                if (var2choice == undefined) {
                    // We've got one variation
                    itemdata = {
                        var1choice: var1choice,
                        quantity: $(this).parents('form').find('input[name="quantity:int"]').val()
                    };
                }
                else {
                    // We've got two variations
                    itemdata = {
                        var1choice: var1choice,
                        var2choice: var2choice,
                        quantity: $(this).parents('form').find('input[name="quantity:int"]').val()
                    };
                }
            }
        }
        else {
            // Get the containing form's action URL
            url = $(this).parent().attr('action');
            // Get skuCode and quantity from adjacent input fields
            itemdata = {
                skuCode: $(this).parents('form').find('input[name="skuCode"]').val(),
                quantity: $(this).parents('form').find('input[name="quantity:int"]').val()
            };
        }

        $.ajax({
        dataType: "json",
        url: url + "_ajax",
        type: "POST",
        cache: false,
        data: itemdata,
        success: function (response) {
            // Add item to cart, receive updated portlet html and translated status message
            var portlet_html = response['portlet_html'];
            var status_message = response['status_message'];
            $('.portletCartPortlet').replaceWith(portlet_html);
            $('#kssPortalMessage').html(status_message);
            $('#kssPortalMessage').fadeIn().animate({opacity: 1.0}, 2000).fadeOut();
            }
        });

        // Reset quantity to 1
        $(this).parents('form').find('input[name="quantity:int"]').val('1');
    });


    // Only show matching item variation depending on user selection
    $(".variation-toplevel-group select").change(function () {
        var uid = $(this).parents("form").find('input[name="uid"]').val();

        var varcode;
        var v2select = $(this).parents("form").find('select[name="var2choice"]');
        if (v2select.length == 0) {
            // We only have one variation
            varcode = "var-" + $(this).parent().find('select[name="var1choice"] option:selected').attr("value");
        }
        else {
            // We've got two variations
            var var1choice = $(this).parents('form').find('select[name="var1choice"] option:selected').attr("value");
            var var2choice = $(this).parents('form').find('select[name="var2choice"] option:selected').attr("value");
            varcode = "var-" + var1choice + "-" + var2choice;

            // Grey out variations that are deactivated
            var other_select = $(this).parents("form").find("select").not($(this));
            if (other_select.attr("name") === "var1choice") {
                var varcode_right_part = $(this).attr("value");
                other_select.find('option').each(function () {
                    var option_val = $(this).attr("value");
                    var option_text = $(this).text();
                    option_vcode = "var-" + $(this).attr("value") + "-" + varcode_right_part;
                    var active = varDicts[uid][option_vcode]['active'];
                    if (active === false) {
                        // add css class "greyed-out"
                        // because IE doesn't detect css class changes in options we remove
                        // the option and add a new one with the desired class.
                        $(this).remove();
                        other_select.append('<option class="greyed-out" value="' + option_val + '">' + option_text + '</option>');
                    }
                    else {
                        // remove css class "greyed-out"
                        // because IE doesn't detect css class changes in options we remove
                        // the option and add a new one without the class attribute.
                        $(this).remove();
                        other_select.append('<option value="' + option_val + '">' + option_text + '</option>');
                    }
                });
                // restore selection
                $(this).parents('form').find('select[name="var1choice"] option[value="'+var1choice+'"]').attr('selected', 'selected');

            }
            else {
                var varcode_left_part = $(this).attr("value");
                other_select.find('option').each(function () {
                    var option_val = $(this).attr("value");
                    var option_text = $(this).text();
                    option_vcode =  "var-" + varcode_left_part + "-" + $(this).attr("value");
                    if (varDicts[uid][option_vcode]['active'] === false) {
                        // add css class "greyed-out"
                        $(this).remove();
                        other_select.append('<option class="greyed-out" value="' + option_val + '">' + option_text + '</option>');
                    }
                    else {
                        // remove css class "greyed-out"
                        $(this).remove();
                        other_select.append('<option value="' + option_val + '">' + option_text + '</option>');
                    }
                });
                // restore selection
                $(this).parents('form').find('select[name="var2choice"] option[value="'+var2choice+'"]').attr('selected', 'selected');
            }
        }

        $(this).parents(".variation-toplevel-group").find("table.itemDataTable tr").hide();

        // Place Price and SKU code directly in variation selection table
        varSelectTable = $(this).parents(".variation-toplevel-group").find("table.variationSelection");
        varPrice = varDicts[uid][varcode]['price'];
        varSkuCode = varDicts[uid][varcode]['skuCode'];
        varDescription = varDicts[uid][varcode]['description'];

        varSelectTable.find("td.variationPrice").text("CHF " + varPrice);
        varSelectTable.find("td.variationSKUCode").text(varSkuCode);
        $(this).parents(".variation-toplevel-group").find("span.variationDescription").text(varDescription);
        $(this).parents(".variation-toplevel-group").find("span.variationDescription").show();

        varSelectTable.find("td.variationPrice").show();
        varSelectTable.find("td.variationSKUCode").show();
        varSelectTable.find("td.variationPriceLabel").show();
        varSelectTable.find("td.variationSKUCodeLabel").show();
        $(this).parents(".variation-toplevel-group").find("table.itemDataTable").hide();

        // Disable "add to cart" button if variation is disabled
        if (varDicts[uid][varcode]['active']) {
            $(this).parents("form").find('input[name="addtocart"]').attr("disabled", false);
            $(this).parents("form").find('input[name="quantity:int"]').attr("disabled", false);

            // Only un-hide the item data if item is active
            $(this).parents(".variation-toplevel-group").find("table.itemDataTable tr").each(function () {
                if (varcode == $(this).attr("id")) {
                    $(this).show();
                }
            });
        }
        else {
            // Inactive variation
            // Hide 'add to cart' button, quantity, price, SKU code and description
            $(this).parents("form").find('input[name="addtocart"]').attr("disabled", true);
            $(this).parents("form").find('input[name="quantity:int"]').attr("disabled", true);
            varSelectTable.find("td.variationPrice").text("");
            varSelectTable.find("td.variationSKUCode").text("");
            $(this).parents(".variation-toplevel-group").find("span.variationDescription").text("");
        }


    }).change();
});
