jq(function () {
	// Add item to cart through AJAX request
	jq('input[name=addtocart]').click(function (event) {
		event.preventDefault();

		if (jq(this).hasClass('compact')) {
			// We're in compact_view, therefore the input's positions inside 
			// the forms are different
			// Get the containing form's action URL
			var url;
			url = jq(this).parents("form").attr('action');
			var var1choice = jq(this).parents("form").find('select[name=var1choice]').find('option:selected').val();
			var var2choice = jq(this).parents("form").find('select[name=var2choice]').find('option:selected').val();
			var itemdata;
			if (var1choice == undefined) {
				// We don't have variations - reference the item by its skuCode
				itemdata = {
					skuCode: jq(this).siblings().filter('input[name=skuCode]').val(),
					quantity: jq(this).siblings().filter('input[name=quantity:int]').val()
				};
			}
			else {
				if (var2choice == undefined) {
					// We've got one variation
					itemdata = {
						var1choice: var1choice,
						quantity: jq(this).parents("form").find('input[name=quantity:int]').val()
					};
				}
				else {
					// We've got two variations
					itemdata = {
						var1choice: var1choice,
						var2choice: var2choice,
						quantity: jq(this).parents("form").find('input[name=quantity:int]').val()
					};
				}
			}
		}
		else {
			// Get the containing form's action URL
			url = jq(this).parent().attr('action');
			// Get skuCode and quantity from adjacent input fields
			itemdata = {
				skuCode: jq(this).siblings().filter('input[name=skuCode]').val(),
				quantity: jq(this).siblings().filter('input[name=quantity:int]').val()
			};
		}

		jq.getJSON(url + "_ajax", itemdata, function (response) {
			// Add item to cart, receive updated portlet html and translated status message
			var portlet_html = response['portlet_html'];
			var status_message = response['status_message'];
			jq('.portletCartPortlet').replaceWith(portlet_html);
			jq('#kssPortalMessage').html(status_message);
			jq('#kssPortalMessage').fadeIn().delay(2000).fadeOut();
		});
	});


	// Only show matching item variation depending on user selection
	jq(".variation-toplevel-group select").change(function () {
		var uid = jq(this).parents("form").find("input[name=uid]").val();

		var varkey;
		var v2select = jq(this).parents("form").find("select[name=var2choice]");
		if (v2select.length == 0) {
			// We only have one variation
			varkey = jq(this).parent().find("select[name=var1choice] option:selected").attr("value");
		}
		else {
			// We've got two variations
			varkey = jq(this).parents("form").find("select[name=var1choice] option:selected").attr("value") + "-" + jq(this).parents("form").find("select[name=var2choice] option:selected").attr("value");

			// Grey out variations that are deactivated
			var other_select = jq(this).parents("form").find("select").not(jq(this));
			if (other_select.attr("name") === "var1choice") {
				var varkey_right_part = jq(this).attr("value");
				other_select.find('option').each(function () {
					option_vkey = jq(this).attr("value") + "-" + varkey_right_part;
					if (varDicts[uid][option_vkey]['active'] === false) {
						jq(this).addClass("greyed-out");
					}
					else {
						jq(this).removeClass("greyed-out");
					}
				})

			}
			else {
				var varkey_left_part = jq(this).attr("value");
				other_select.find('option').each(function () {
					option_vkey =  varkey_left_part + "-" + jq(this).attr("value");
					if (varDicts[uid][option_vkey]['active'] === false) {
						jq(this).addClass("greyed-out");
					}
					else {
						jq(this).removeClass("greyed-out");
					}
				})
			}
		}

		jq(this).parents(".variation-toplevel-group").find("table.itemDataTable tr").hide();

		// Place Price and SKU code directly in variation selection table
		varSelectTable = jq(this).parents(".variation-toplevel-group").find("table.variationSelection");
		varPrice = varDicts[uid][varkey]['price']
		varSkuCode = varDicts[uid][varkey]['skuCode']
		varDescription = varDicts[uid][varkey]['description']

		varSelectTable.find("td.variationPrice").text(varPrice);
		varSelectTable.find("td.variationSKUCode").text(varSkuCode);
		jq(this).parents(".variation-toplevel-group").find("span.variationDescription").text(varDescription);
		jq(this).parents(".variation-toplevel-group").find("span.variationDescription").show();

		varSelectTable.find("td.variationPrice").show();
		varSelectTable.find("td.variationSKUCode").show();
		varSelectTable.find("td.variationPriceLabel").show();
		varSelectTable.find("td.variationSKUCodeLabel").show();
		jq(this).parents(".variation-toplevel-group").find("table.itemDataTable").hide();

		// Disable "add to cart" button if variation is disabled
		if (varDicts[uid][varkey]['active']) {
			jq(this).parents("form").find("input[name=addtocart]").attr("disabled", false);
			jq(this).parents("form").find("input[name=quantity:int]").attr("disabled", false);

			// Only un-hide the item data if item is active
			jq(this).parents(".variation-toplevel-group").find("table.itemDataTable tr").each(function () {
				if (varkey == jq(this).attr("id")) {
					jq(this).show();
				}
			});
		}
		else {
			// Inactive variation
			// Hide 'add to cart' button, quantity, price, SKU code and description
			jq(this).parents("form").find("input[name=addtocart]").attr("disabled", true);
			jq(this).parents("form").find("input[name=quantity:int]").attr("disabled", true);
			varSelectTable.find("td.variationPrice").text("");
			varSelectTable.find("td.variationSKUCode").text("");
			jq(this).parents(".variation-toplevel-group").find("span.variationDescription").text("");
		}


	}).change();
});