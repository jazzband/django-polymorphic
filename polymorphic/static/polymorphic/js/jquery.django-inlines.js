/**
 * jQuery plugin for Django inlines
 *
 * (c) 2011-2016 Diederik van der Boor, Apache 2 Licensed.
 */

(function($){

  function DjangoInline(group, options) {
    options = $.extend({}, $.fn.djangoInline.defaults, options);

    this.group = group;
    this.$group = $(group);
    this.options = options;

    options.prefix = options.prefix || this.$group.attr('id').replace(/-group$/, '');

    if( options.formTemplate ) {
      this.$form_template = $(options.formTemplate);
    } else {
      this.$form_template = this.$group.find(this.options.emptyFormSelector);  // the extra item to construct new instances.
    }

    // Create the add button if requested (null/undefined means auto select)
    if(options.showAddButton !== false) {
      var dominfo = this._getManagementForm();
      if (dominfo.max_forms == null || dominfo.max_forms.value === '' || (dominfo.max_forms.value - dominfo.total_forms.value) > 0) {
        this.createAddButton();
      }
    }
  }

  DjangoInline.prototype = {

    /**
     * Create the add button
     */
    createAddButton: function() {
      var $addButton;
      var myself = this;
      if (this.options.childTypes) {
        // Polymorphic inlines!
        // The add button opens a menu.
        var menu = '<div class="inline-type-choice" style="display: none;"><ul>';
        for (var i = 0; i < this.options.childTypes.length; i++) {
          var obj = this.options.childTypes[i];
          menu += '<li><a href="#" data-type="' + obj.type + '">' + obj.name + '</a></li>';
        }
        menu += '</ul></div>';
        $addButton = $('<div class="' + this.options.addCssClass + ' add-row-choice"><a href="#">' + this.options.addText + "</a>" + menu + "</div>");
        this.$group.append($addButton);

        $addButton.children('a').click($.proxy(this._onMenuToggle, this));
        $addButton.find('li a').click(function(event){ myself._onMenuItemClick(event); });
      }
      else {
        // Normal inlines
        $addButton = $('<div class="' + this.options.addCssClass + '"><a href="#">' + this.options.addText + "</a></div>");
        this.$group.append($addButton);

        $addButton.find('a').click(function(event) { event.preventDefault(); myself.addForm() });
      }
    },

    _onMenuToggle: function(event) {
      event.preventDefault();
      event.stopPropagation();
      var $menu = $(event.target).next('.inline-type-choice');

      if(! $menu.is(':visible')) {
        function hideMenu() {
          $menu.slideUp();
          $(document).unbind('click', hideMenu);
        }

        $(document).click(hideMenu);
      }

      $menu.slideToggle();
    },

    _onMenuItemClick: function(event) {
      event.preventDefault();
      var type = $(event.target).attr('data-type');
      var empty_form_selector = this.options.emptyFormSelector + "[data-inline-type=" + type + "]";
      this.addForm(empty_form_selector);
    },

    /**
     * The main action, add a new row.
     * Allow to select a different form template (for polymorphic inlines)
     */
    addForm: function(emptyFormSelector) {
      var $form_template;

      if(emptyFormSelector) {
        $form_template = this.$group.find(emptyFormSelector);
        if($form_template.length === 0) {
          throw new Error("Form template '" + emptyFormSelector + "' not found")
        }
      }
      else {
        if(! this.$form_template || this.$form_template.length === 0) {
          throw new Error("No empty form available. Define the 'form_template' setting or add an '.empty-form' element in the '" + this.options.prefix + "' formset group!");
        }

        $form_template = this.$form_template;
      }

      // The Django admin/media/js/inlines.js API is not public, or easy to use.
      // Recoded the inline model dynamics.
      var management_form = this._getManagementForm();
      if(! management_form.total_forms) {
        throw new Error("Missing '#" + this._getGroupFieldIdPrefix() + "-TOTAL_FORMS' field. Make sure the management form included!");
      }

      // When a inline is presented in a complex table,
      // the newFormTarget can be very useful to direct the output.
      var container;
      if(this.options.newFormTarget == null) {
        container = $form_template.parent();
      }
      else if($.isFunction(this.options.newFormTarget)) {
        container = this.options.newFormTarget.apply(this.group);
      }
      else {
        container = this.$group.find(this.options.newFormTarget);
      }

      if(container === null || container.length === 0) {
        throw new Error("No container found via custom 'newFormTarget' function!");
      }

      // Clone the item.
      var new_index = management_form.total_forms.value;
      var item_id   = this._getFormId(new_index);
      var newhtml = _getOuterHtml($form_template).replace(/__prefix__/g, new_index);
      var newitem = $(newhtml).removeClass("empty-form").attr("id", item_id);

      // Add it
      container.append(newitem);
      var formset_item = $("#" + item_id);
      if( formset_item.length === 0 ) {
        throw new Error("New FormSet item not found: #" + item_id);
      }

      formset_item.data('djangoInlineIndex', new_index);
      if(this.options.onAdd) {
        this.options.onAdd.call(this.group, formset_item, new_index, this.options);
      }

      // Update administration
      management_form.total_forms.value++;
      return formset_item;
    },

    getFormAt: function(index) {
      return $('#' + this._getFormId(index));
    },

    _getFormId: function(index) {
      // The form container is expected by the numbered as #prefix-NR
      return this.options.itemIdTemplate.replace('{prefix}', this.options.prefix).replace('{index}', index);
    },

    _getGroupFieldIdPrefix: function() {
      // typically:  #id_modelname
      return this.options.autoId.replace('{prefix}', this.options.prefix);
    },

    /**
     * Get the management form data.
     */
    _getManagementForm: function() {
      var group_id_prefix = this._getGroupFieldIdPrefix();
      return {
        // management form item
        total_forms: $("#" + group_id_prefix + "-TOTAL_FORMS")[0],
        max_forms: $("#" + group_id_prefix + "-MAX_NUM_FORMS")[0],
        group_id_prefix: group_id_prefix
      }
    },

    _getItemData: function(child_node) {
      var formset_item = $(child_node).closest(this.options.itemsSelector);
      if( formset_item.length === 0 ) {
        return null;
      }

      // Split the ID, using the id_template pattern.
      // note that ^...$ is important, as a '-' char can occur multiple times with generic inlines (inlinetype-id / app-model-ctfield-ctfkfield-id)
      var id = formset_item.attr("id");
      var cap = (new RegExp('^' + this.options.itemIdTemplate.replace('{prefix}', '(.+?)').replace('{index}', '(\\d+)') + '$')).exec(id);

      return {
        formset_item: formset_item,
        prefix: cap[1],
        index: parseInt(cap[2], 0)   // or parseInt(formset_item.data('djangoInlineIndex'))
      };
    },

    /**
     * Get the meta-data of a single form.
     */
    _getItemForm: function(child_node) {
      var dominfo = this._getItemData(child_node);
      if( dominfo === null ) {
        return null;
      }

      var field_id_prefix = this._getGroupFieldIdPrefix() + "-" + dominfo.index;
      return $.extend({}, dominfo, {
        // Export settings data
        field_id_prefix: field_id_prefix,
        field_name_prefix: dominfo.prefix + '-' + dominfo.index,

        // Item fields
        pk_field: $('#' + field_id_prefix + '-' + this.options.pkFieldName),
        delete_checkbox: $("#" + field_id_prefix + "-DELETE")
      });
    },

    /**
     * Remove a row
     */
    removeForm: function(child_node)
    {
      // Get dom info
      var management_form = this._getManagementForm();
      var itemform = this._getItemForm(child_node);
      if( itemform === null ) {
        throw new Error("No form found for the selector '" + child_node.selector + "'!");
      }

      var total_count = parseInt(management_form.total_forms.value, 0);
      var has_pk_field = itemform.pk_field.length != 0;

      if(this.options.onBeforeRemove) {
        this.options.onBeforeRemove.call(this.group, itemform.formset_item, this.options);
      }

      // In case there is a delete checkbox, save it.
      if( itemform.delete_checkbox.length )
      {
        if(has_pk_field)
          itemform.pk_field.insertAfter(management_form.total_forms);
        itemform.delete_checkbox.attr('checked', true).insertAfter(management_form.total_forms).hide();
      }
      else if( has_pk_field && itemform.pk_field[0].value )
      {
        // Construct a delete checkbox on the fly.
        itemform.pk_field.insertAfter(management_form.total_forms);
        $('<input type="hidden" id="' + itemform.field_id_prefix + '-DELETE" name="' + itemform.field_name_prefix + '-DELETE" value="on">').insertAfter(itemform.total_forms);
      }
      else
      {
        // Newly added item, renumber in reverse order
        for( var i = itemform.index + 1; i < total_count; i++ )
        {
          this._renumberItem(this.getFormAt(i), i - 1);
        }

        management_form.total_forms.value--;
      }


      // And remove item
      itemform.formset_item.remove();

      if(this.options.onRemove) {
        this.options.onRemove.call(this.group, itemform.formset_item, this.options);
      }

      return itemform.formset_item;
    },

    // Based on django/contrib/admin/media/js/inlines.js
    _renumberItem: function($formset_item, new_index)
    {
      var id_regex = new RegExp("(" + this._getFormId('(\\d+|__prefix__)') + ")");
      var replacement = this._getFormId(new_index);
      $formset_item.data('djangoInlineIndex', new_index);

      // Loop through the nodes.
      // Getting them all at once turns out to be more efficient, then looping per level.
      var nodes = $formset_item.add( $formset_item.find("*") );
      for( var i = 0; i < nodes.length; i++ )
      {
        var node = nodes[i];
        var $node = $(node);

        var for_attr = $node.attr('for');
        if( for_attr && for_attr.match(id_regex) ) {
          $node.attr("for", for_attr.replace(id_regex, replacement));
        }

        if( node.id && node.id.match(id_regex) ) {
          node.id = node.id.replace(id_regex, replacement);
        }

        if( node.name && node.name.match(id_regex) ) {
          node.name = node.name.replace(id_regex, replacement);
        }
      }
    },

    // Extra query methods for external callers:

    getFormIndex: function(child_node) {
      var dominfo = this._getItemData(child_node);
      return dominfo ? dominfo.index : null;
    },

    getForms: function() {
      // typically:  .inline-related:not(.empty-form)
      return this.$group.children(this.options.itemsSelector + ":not(" + this.options.emptyFormSelector + ")");
    },

    getEmptyForm: function() {
      // typically:  #modelname-group > .empty-form
      return this.$form_template;
    },

    getFieldIdPrefix: function(item_index) {
      if(! $.isNumeric(item_index)) {
        var dominfo = this._getItemData(item_index);
        if(dominfo === null) {
          throw new Error("Unexpected element in getFieldIdPrefix, needs to be item_index, or DOM child node.");
        }
        item_index = dominfo.index;
      }

      // typically:  #id_modelname-NN
      return this._getGroupFieldIdPrefix() + "-" + item_index;
    },

    getFieldsAt: function(index) {
      var $form = this.getFormAt(index);
      return this.getFields($form);
    },

    getFields: function(child_node) {
      // Return all fields in a simple lookup object, with the prefix stripped.
      var dominfo = this._getItemData(child_node);
      if(dominfo === null) {
        return null;
      }

      var fields = {};
      var $inputs = dominfo.formset_item.find(':input');
      var name_prefix = this.prefix + "-" + dominfo.index;

      for(var i = 0; i < $inputs.length; i++) {
        var name = $inputs[i].name;
        if(name.substring(0, name_prefix.length) == name_prefix) {
          var suffix = name.substring(name_prefix.length + 1);  // prefix-<name>
          fields[suffix] = $inputs[i];
        }
      }

      return fields;
    },

    removeFormAt: function(index) {
      return this.removeForm(this.getFormAt(index));
    }
  };


  function _getOuterHtml($node)
  {
    if( $node.length )
    {
      if( $node[0].outerHTML ) {
        return $node[0].outerHTML;
      } else {
        return $("<div>").append($node.clone()).html();
      }
    }
    return null;
  }


  // jQuery plugin definition
  // Separated from the main code, as demonstrated by Twitter bootstrap.
  $.fn.djangoInline = function(option) {
    var args = Array.prototype.splice.call(arguments, 1);
    var call_method = (typeof option == 'string');
    var plugin_result = (call_method ? undefined : this);

    this.filter('.inline-group').each(function() {
      var $this = $(this);
      var data = $this.data('djangoInline');

      if (! data) {
        var options = typeof option == 'object' ? option : {};
        $this.data('djangoInline', (data = new DjangoInline(this, options)));
      }

      if (typeof option == 'string') {
        plugin_result = data[option].apply(data, args);
      }
    });

    return plugin_result;
  };

  $.fn.djangoInline.defaults = {
    pkFieldName: 'id',       // can be `tablename_ptr` for inherited models.
    autoId: 'id_{prefix}',   // the auto id format used in Django.
    prefix: null,            // typically the model name in lower case.
    newFormTarget: null,     // Define where the row should be added; a CSS selector or function.

    itemIdTemplate: '{prefix}-{index}',  // Format of the ID attribute.
    itemsSelector:  '.inline-related',   // CSS class that each item has
    emptyFormSelector: '.empty-form',    // CSS class that

    formTemplate: null,  // Complete HTML of the new form
    childTypes: null,    // Extra for django-polymorphic, allow a choice between empty-forms.

    showAddButton: true,
    addText: "add another",      // Text for the add link
    deleteText: "remove",      // Text for the delete link
    addCssClass: "add-row"      // CSS class applied to the add link
  };

  // Also expose inner object
  $.fn.djangoInline.Constructor = DjangoInline;


  // Auto enable inlines
  $.fn.ready(function(){
    $('.js-jquery-django-inlines').each(function(){
      var $this = $(this);
      var data = $this.data();
      var inlineOptions = data.inlineFormset;
      $this.djangoInline(inlineOptions.options)
    });
  })
})(window.django ? window.django.jQuery : jQuery);
