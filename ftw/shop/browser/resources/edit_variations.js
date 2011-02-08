jq(function () {
    // toggle
    var span='';
    
    if (jq('.showConfigVariations').attr('value')==1) {
        toggleVariations();
    }
    
    jq("#content dl.toggleVariation dt").click(function () {
        toggleVariations();
    });
    
    function toggleVariations() {
        jq('#content dl.toggleVariation dd').slideToggle();
        jq('span.toggleHead').toggleClass('collapsed');
    }
    
    var update_vcodes = function () {
        // Updates all vcodes in the inputs name attributes
        jq('.varTable').each(function(tbl_idx, tbl) {
            var rows = jq(tbl).find('tr');
            rows.each(function(row_idx, row) {
                var vcode = tbl_idx + '-' + (row_idx - 1)
                var inputs = jq(row).find('input');
                inputs.each(function() {
                    if (jq(this).hasClass('attributeLabelInput')) {
                        var new_name = "v2-value-" + (row_idx - 1);
                    }
                    else {
                        var old_name = jq(this).attr('name');
                        var old_v1idx = old_name.split('-')[1];
                        var old_v2idx = old_name.split('-')[2];
                        var old_vcode = old_v1idx + '-' + old_v2idx;
                        var new_name = old_name.replace(old_vcode, vcode);
                    }
                    jq(this).attr('name', new_name);
                });
            });
        });
    };

      // Add a new attribute
      jq('.add-attribute').live('click', function(event) {
          var attr_template = jq('.attribute-template');
          attr_template.removeClass('attribute-template');
          attr_template.addClass('attribute');
          attr_template.css('display', 'block');
      });

      // Toggle disabled status of the row's input fields
      jq('.varActiveCheckbox').live('click', function(event) {
          var row = jq(this).parents('tr');
          row.find('input').not('.varActiveCheckbox').not('.attributeLabelInput').each(function() {
              var current_val = jq(this).attr('disabled');
              if (current_val === true) {
                  jq(this).removeAttr('disabled');
              }
              else {
                  jq(this).attr('disabled', true);
              }
          });
          row.toggleClass('greyed-out');
      });

      // Add a new variant
      jq('.add-variant').live('click', function(event) {
          var clicked_row = jq(this).parents('tr');
          var vcode = clicked_row.find('input').first().attr('name').replace('-active:boolean', '').replace('var-', '');
          var v1_idx = parseInt(vcode.split('-')[0]);
          var v2_idx = parseInt(vcode.split('-')[1]);
          var row_from_first_table = jq(jq('form#variations table').first().find('tr')[v2_idx + 1]);

          var tables = jq('.varTable');
          tables.each(function(tbl_idx, tbl_element) {
              var rows = jq(this).find('tr');
              var matching_row = jq(rows[v2_idx + 1]); // + 1 because first one is header row
              var new_row = matching_row.clone();
              matching_row.after(new_row);
              new_row.find('input').each(function() {
                  jq(this).val('');
              });
              new_row.find('.attribute-label').first().text('Neue Variante');

          });
          var added_row = row_from_first_table.next();
          added_row.find('.attributeLabelInput').val('Neue Variante');

          update_vcodes();

      });


      // Delete a variant
      jq('.del-variant').live('click', function(event) {
          var clicked_row = jq(this).parents('tr');
          var vcode = clicked_row.find('input').first().attr('name').replace('-active:boolean', '').replace('var-', '');
          var v1_idx = parseInt(vcode.split('-')[0]);
          var v2_idx = parseInt(vcode.split('-')[1]);
          var row_from_first_table = jq(jq('form#variations table').first().find('tr')[v2_idx + 1]);

          var tables = jq('.varTable');
          tables.each(function(tbl_idx, tbl_element) {
              var rows = jq(this).find('tr');
              var matching_row = jq(rows[v2_idx + 1]); // + 1 because first one is header row
              matching_row.remove();
          });

          update_vcodes();

      });

      // Delete an attribute
      jq('.del-attribute').live('click', function(event) {
          var attr = jq(this).parent();
          attr.slideUp().delay(500).remove();
      });

      // Store old variant name if it's about to be renamed
      jq('input.attributeLabelInput').live('focus', function(event) {
          jq(this).data('old_value', jq(this).val());
      });

      // Rename all occurences of the variant
      jq('input.attributeLabelInput').live('change', function(event) {
          var new_variant_name = jq(this).val();
          var v2_idx = parseInt(jq(this).attr('name').replace('v2-value-', ''));
          var linked_labels = jq('.varTable tr:nth-child(' + (v2_idx + 1) +') .attribute-label');

          jq(linked_labels).each(function () {
              var el = jq(this);
              el.text(new_variant_name);
          });

      });
      
    // Make the combinations sortable by the user
    jq(".sortable").sortable({
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
    jq("form#variations input[type=checkbox]").not(":checked").each(function () {
              var row = jq(this).parents('tr');
              row.find('input').not('.varActiveCheckbox').not('.attributeLabelInput').each(function() {
                  var current_val = jq(this).attr('disabled');
                  if (current_val === true) {
                      jq(this).removeAttr('disabled');
                  }
                  else {
                      jq(this).attr('disabled', true);
                  }
              });
              row.toggleClass('greyed-out');
    });

  });