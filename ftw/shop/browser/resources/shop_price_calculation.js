// Calculate price per item
function calculatePrice() {
    var context = $(this).closest('.shopItem, .cartListing tr');
    var dimensions = $("input[name^='dimension']", context).map(function() {
        var number = parseFloat($(this).val());
        // it's not possible to check for NaN with indexOf (NaN != NaN). so convert it to false
        return (!isNaN(number)) ? number : false;
    }).toArray();

    var formatted_price = "-";

    if (dimensions.indexOf(false) === -1) {
        var volume = dimensions.reduce(function(a, b) {return a*b;});
        var itemData = $('.dimensions-selection', context).data();

        if (itemData.hasOwnProperty('price')) {
            var price = itemData.price;
        } else {
            // the price is unknown at render time if the item has variations
            var price = parseFloat($('.price', context).text());
        }

        var pricePerItem = price / itemData.priceToDimensionModifier * volume;

        // round up
        pricePerItem = Math.ceil(pricePerItem * 100) / 100;
        formatted_price = pricePerItem.toLocaleString('de-CH', {minimumFractionDigits: 2});
    }

    $('.item-price', context).text(formatted_price);
}

$(document).on('input', ".dimensions-selection input[name^='dimension']", calculatePrice);
$(document).on('change', ".variationSelection select", calculatePrice);
