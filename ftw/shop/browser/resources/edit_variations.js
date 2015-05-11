jQuery(function ($) {
    // toggle
    $("#content dl.toggleVariation dt").click(function () {
        $(this).next().slideToggle();
    });

    var update_vcodes = function () {
        // Updates all vcodes in the inputs name attributes
        $('.varTable').each(function(tbl_idx, tbl) {
            var rows = $(tbl).find('tr');
            rows.each(function(row_idx, row) {
                var vcode = tbl_idx + '-' + (row_idx - 1)
                var inputs = $(row).find('input');
                inputs.each(function() {
                    if ($(this).hasClass('attributeLabelInput')) {
                        var new_name = "v2-value-" + (row_idx - 1);
                    }
                    else {
                        var old_name = $(this).attr('name');
                        var old_v1idx = old_name.split('-')[1];
                        var old_v2idx = old_name.split('-')[2];
                        var old_vcode = old_v1idx + '-' + old_v2idx;
                        var new_name = old_name.replace(old_vcode, vcode);
                    }
                    $(this).attr('name', new_name);
                });
            });
        });
    };

      // Add a new attribute
      $('.add-attribute').live('click', function(event) {
          var attr_template = $('.attribute-template');
          attr_template.removeClass('attribute-template');
          attr_template.addClass('attribute');
          attr_template.css('display', 'block');
      });

      // Toggle disabled status of the row's input fields
      $('.varActiveCheckbox').live('click', function(event) {
          var row = $(this).parents('tr');
          row.find('input').not('.varActiveCheckbox').not('.attributeLabelInput').each(function() {
              if ($(this).is(":disabled")) {
                  $(this).removeAttr('disabled');
              }
              else {
                  $(this).attr('disabled', true);
              }
          });
          row.toggleClass('greyed-out');
      });

      // Add a new variant
      $('.add-variant').live('click', function(event) {
          var clicked_row = $(this).parents('tr');
          var vcode = clicked_row.find('input').first().attr('name').replace('-active:boolean', '').replace('var-', '');
          var v1_idx = parseInt(vcode.split('-')[0]);
          var v2_idx = parseInt(vcode.split('-')[1]);
          var row_from_first_table = $($('form#variations table').first().find('tr')[v2_idx + 1]);

          var tables = $('.varTable');
          tables.each(function(tbl_idx, tbl_element) {
              var rows = $(this).find('tr');
              var matching_row = $(rows[v2_idx + 1]); // + 1 because first one is header row
              var new_row = matching_row.clone();
              matching_row.after(new_row);
              new_row.find('input').each(function() {
                  $(this).val('');
              });
              new_row.find('.attribute-label').first().text('Neue Variante');

          });
          var added_row = row_from_first_table.next();
          added_row.find('.attributeLabelInput').val('Neue Variante');

          update_vcodes();

      });


      // Delete a variant
      $('.del-variant').live('click', function(event) {
          var clicked_row = $(this).parents('tr');
          var vcode = clicked_row.find('input').first().attr('name').replace('-active:boolean', '').replace('var-', '');
          var v1_idx = parseInt(vcode.split('-')[0]);
          var v2_idx = parseInt(vcode.split('-')[1]);
          var row_from_first_table = $($('form#variations table').first().find('tr')[v2_idx + 1]);

          var tables = $('.varTable');
          tables.each(function(tbl_idx, tbl_element) {
              var rows = $(this).find('tr');
              var matching_row = $(rows[v2_idx + 1]); // + 1 because first one is header row
              matching_row.remove();
          });

          update_vcodes();

      });

      // Delete an attribute
      $('.del-attribute').live('click', function(event) {
          var attr = $(this).parent();
          attr.slideUp().delay(500).remove();
      });

      // Store old variant name if it's about to be renamed
      $('input.attributeLabelInput').live('focus', function(event) {
          $(this).data('old_value', $(this).val());
      });

      // Rename all occurences of the variant
      $('input.attributeLabelInput').live('change', function(event) {
          var new_variant_name = $(this).val();
          var v2_idx = parseInt($(this).attr('name').replace('v2-value-', ''));
          var linked_labels = $('.varTable tr:nth-child(' + (v2_idx + 1) +') .attribute-label');

          $(linked_labels).each(function () {
              var el = $(this);
              el.text(new_variant_name);
          });

      });

    // Make the combinations sortable by the user
    $(".sortable").sortable({
     revert: true,
     handle: ".drag-variant",
     axis: "y",
     opacity: 0.8,
     containment: "parent",
     update: function(event, ui) {
         update_vcodes();
     }

    });

    // Disabled all inactive rows on page load
    $("form#variations input[type=checkbox]").not(":checked").each(function () {
              var row = $(this).parents('tr');
              row.find('input').not('.varActiveCheckbox').not('.attributeLabelInput').each(function() {
                  var current_val = $(this).attr('disabled');
                  if (current_val === true) {
                      $(this).removeAttr('disabled');
                  }
                  else {
                      $(this).attr('disabled', true);
                  }
              });
              row.toggleClass('greyed-out');
    });

  });
