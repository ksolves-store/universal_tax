/** @odoo-module */
//

import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { patch } from "@web/core/utils/patch";
import { formatFloat, formatMonetary } from "@web/views/fields/formatters";
import { TaxTotalsComponent } from "@account/components/tax_totals/tax_totals";
//
const { Component, onPatched, onWillUpdateProps, useRef, useState } = owl;

patch(TaxTotalsComponent.prototype, "amount_addition", {
    formatData(props)  {
        if (!this.totals) {
            return;
        }

//        this.totals = nextProps.value;
//        this.readonly = nextProps.readonly;
        let totals = structuredClone(props.value);
        const currencyFmtOpts = { currencyId: props.record.data.currency_id && props.record.data.currency_id[0] };

        let amount_untaxed = totals.amount_untaxed;

        let amount_tax = 0;
        let subtotals = [];
        for (let subtotal_title of totals.subtotals_order) {
            let amount_total = amount_untaxed + amount_tax ;
            subtotals.push({
                'name': subtotal_title,
                'amount': amount_total,
                'formatted_amount': formatMonetary(amount_total,currencyFmtOpts),
            });
            let group = totals.groups_by_subtotal[subtotal_title];
            for (let i in group) {
                amount_tax = amount_tax + group[i].tax_group_amount;
            }
        }
        totals.subtotals = subtotals;
        let amount_total = amount_untaxed + amount_tax + this.props.record.data.ks_amount_global_tax;
        totals.ks_tax_amount = formatMonetary(this.props.record.data.ks_amount_global_tax)
        totals.amount_total = amount_total;
        totals.formatted_amount_total = formatMonetary(amount_total,currencyFmtOpts);



        for (let group_name of Object.keys(totals.groups_by_subtotal)) {
            let group = totals.groups_by_subtotal[group_name];
            for (let i in group) {
                group[i].formatted_tax_group_amount = formatMonetary(group[i].tax_group_amount);
                group[i].formatted_tax_group_base_amount = formatMonetary(group[i].tax_group_base_amount);
            }
        }
         this.totals = totals;
    }
})