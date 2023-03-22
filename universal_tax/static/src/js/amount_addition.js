/** @odoo-module */
//

import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { patch } from "@web/core/utils/patch";
import { TaxTotalsComponent } from "@account/components/tax_totals/tax_totals";
//
const { Component, onPatched, onWillUpdateProps, useRef, useState } = owl;

//TaxTotalsComponent.props = {
//    ...standardFieldProps,
//}

patch(TaxTotalsComponent.prototype, "amount_addition", {
    _computeTotalsFormat() {
        if (!this.totals) {
            return;
        }
        let amount_untaxed = this.totals.amount_untaxed;
        let amount_tax = 0;
        let subtotals = [];
        for (let subtotal_title of this.totals.subtotals_order) {
            let amount_total = amount_untaxed + amount_tax ;
            subtotals.push({
                'name': subtotal_title,
                'amount': amount_total,
                'formatted_amount': this._format(amount_total),
            });
            let group = this.totals.groups_by_subtotal[subtotal_title];
            for (let i in group) {
                amount_tax = amount_tax + group[i].tax_group_amount;
            }
        }
        this.totals.subtotals = subtotals;
        let amount_total = amount_untaxed + amount_tax +this.props.record.data.ks_amount_global_tax;
        this.totals.amount_total = amount_total;
        this.totals.formatted_amount_total = this._format(amount_total);
        for (let group_name of Object.keys(this.totals.groups_by_subtotal)) {
            let group = this.totals.groups_by_subtotal[group_name];
            for (let i in group) {
                group[i].formatted_tax_group_amount = this._format(group[i].tax_group_amount);
                group[i].formatted_tax_group_base_amount = this._format(group[i].tax_group_base_amount);
            }
        }
    }
})