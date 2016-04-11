/*!
 * Ext JS Library 3.4.0
 * Copyright(c) 2006-2011 Sencha Inc.
 * licensing@sencha.com
 * http://www.sencha.com/license
 */
Ext.ns('Ext.ux.form');

Ext.ux.form.SearchField = Ext.extend(Ext.form.TwinTriggerField, {
    initComponent : function(){
        Ext.ux.form.SearchField.superclass.initComponent.call(this);
        this.on('specialkey', function(f, e){
            if(e.getKey() == e.ENTER){
                this.onTrigger2Click();
            }
        }, this);
    },

    validationEvent:false,
    validateOnBlur:false,
    trigger1Class:'x-form-clear-trigger',
    trigger2Class:'x-form-search-trigger',
    hideTrigger1:true,
    width:180,
    hasSearch : false,
    paramName : 'CQL_FILTER',

    onTrigger1Click : function(){
        if(this.hasSearch){
            this.el.dom.value = '';
            var o = {start: 0};
            this.store.baseParams = this.store.baseParams || {};
            this.store.baseParams[this.paramName] = 'None';
            this.store.reload({params:o});
            this.triggers[0].hide();
            this.hasSearch = false;
        }
    },

    onTrigger2Click : function(){
        var v = this.getRawValue();
        // if(v.length < 1){
        //     this.onTrigger1Click();
        //     return;
        // }
        v = v.toLowerCase();
        var layers = [];
        var filters = []
        var addQS = "";
        var addQH = "";
        // console.log(Ext.getCmp('districtSelectionLocator').getValue());
        if (Ext.getCmp('provSelectionLocator').getValue() != ''){
            addQS = " AND prov_code_1="+Ext.getCmp('provSelectionLocator').value ;
            addQH = " AND prov_code="+Ext.getCmp('provSelectionLocator').value ;
        } //else {
          //  this.onTrigger1Click();
          //  return;
        //}

        if (Ext.getCmp('districtSelectionLocator').getValue() != '' ){
            addQS = " AND dist_code="+Ext.getCmp('districtSelectionLocator').value ;
            addQH = " AND dist_code="+Ext.getCmp('districtSelectionLocator').value ;
        }
        
        
        if (Ext.getCmp('settlementCB').checked){
            layers.push('geonode:afg_pplp');
            filters.push("strToLowerCase(name_en) like '%"+v+"%'"+addQS);
        }
        if (Ext.getCmp('hfCB').checked){
            layers.push('geonode:afg_hltfac');
            filters.push("strToLowerCase(facility_name) like '%"+v+"%'"+addQH);
        }
        if (Ext.getCmp('airportCB').checked){
            layers.push('geonode:afg_airdrmp');
            filters.push("strToLowerCase(namelong) like '%"+v+"%'"+addQH);
        }

        var typeName = '';
        var queryFilter = '';
        for (var i=0;i<layers.length;i++){
            if (layers.length>1 && i!=layers.length-1){
                typeName += layers[i] + ',';
                queryFilter += filters[i] + ';';
            } else {
                typeName += layers[i];
                queryFilter += filters[i];
            }
        }

        // console.log(Ext.getCmp('districtSelectionLocator').getValue());

        if(Ext.getCmp('settlementCB').checked) {   
            if(v.length < 1 && Ext.getCmp('districtSelectionLocator').getValue() == ''){
                this.onTrigger1Click();
                return;
            }
        } else {
            if(v.length < 1 &&  Ext.getCmp('provSelectionLocator').getValue() == ''){
                this.onTrigger1Click();
                return;
            }
        }

        // var test = "strToLowerCase(name_en) like '"+v+"%'";
        var o = {start: 0};
        this.store.baseParams = this.store.baseParams || {};
        this.store.baseParams[this.paramName] = queryFilter;
        this.store.baseParams['typeName'] = typeName;
        this.store.reload({params:o});
        this.hasSearch = true;
        this.triggers[0].show();
    }
});