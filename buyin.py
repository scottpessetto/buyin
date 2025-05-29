def model_rsu_scheme(grant_size, annual_return_percentage, simulation_years=10, return_decay_rate_per_year=0.0):
    """
    Models an RSU scheme over a number of years, with an option for declining returns on older grants.

    Args:
        grant_size (float): The value of the new grant received each year.
        annual_return_percentage (float): The initial annual return as a decimal (e.g., 0.10 for 10%).
        simulation_years (int): The number of years to simulate.
        return_decay_rate_per_year (float): The rate at which the annual return percentage
                                            decays for a grant each year after its first year
                                            of earning. E.g., 0.01 means a 1% reduction
                                            of the previous year's effective rate.
                                            (0.0 means no decay).

    Returns:
        list: A list of dictionaries, where each dictionary contains
              'year', 'total_cash_received', 'total_withheld_balance_end_of_year',
              and a detailed breakdown.
    """
    active_grants = []  # Stores details of each grant
    yearly_cash_summary = []  # Stores summary for each simulation year

    print(f"--- RSU Model Configuration ---")
    print(f"Annual Grant Size: ${grant_size:,.2f}")
    print(f"Initial Annual Return Rate: {annual_return_percentage*100:.2f}% on grant value")
    if return_decay_rate_per_year > 0:
        print(f"Return Decay Rate Per Year (after 1st year of return): {return_decay_rate_per_year*100:.2f}%")
    else:
        print(f"Return Decay Rate Per Year: No decay")
    print(f"Simulation Period: {simulation_years} years")
    print("---------------------------------\n")

    # Loop through each year of the simulation
    for current_sim_year in range(1, simulation_years + 1):
        print(f"--- Processing Year {current_sim_year} ---")

        year_cash_details = {"direct_from_returns": 0.0, "payouts_from_withheld": 0.0, "log": []}

        # 1. Issue a new grant
        new_grant = {
            "id": current_sim_year,
            "value": grant_size,
            "accumulated_withheld": 0.0,
            "age_in_years": 0,  # Will be incremented to 1 when it first earns
            "payout_occurred": False,
        }
        active_grants.append(new_grant)
        year_cash_details["log"].append(f"  New grant G{new_grant['id']} (value ${new_grant['value']:,.2f}) issued.")

        current_year_total_cash_to_employee = 0.0

        # 2. Process returns and withholding for all active grants
        for grant in active_grants:
            grant["age_in_years"] += 1  # Increment age as it's processing for the current year
            grant_log_prefix = f"  Grant G{grant['id']} (Age: {grant['age_in_years']}, Value: ${grant['value']:,.2f}):"

            # Calculate effective return rate for this grant for this year
            effective_return_rate = annual_return_percentage
            if grant["age_in_years"] > 1 and return_decay_rate_per_year > 0:
                # Apply decay for years after the first year the grant earns a return
                # The power is (age_in_years - 1) because the first year of return has no decay.
                decay_factor = (1 - return_decay_rate_per_year) ** (grant["age_in_years"] - 1)
                effective_return_rate *= decay_factor
                # Ensure rate doesn't go negative, though with (1-rate) it shouldn't unless rate > 1
                effective_return_rate = max(0, effective_return_rate)

            current_grant_return = grant["value"] * effective_return_rate

            if current_grant_return == 0:
                year_cash_details["log"].append(
                    f"{grant_log_prefix} No return this year (Effective rate: {effective_return_rate*100:.2f}%)."
                )
                continue

            year_cash_details["log"].append(
                f"{grant_log_prefix} Earned ${current_grant_return:,.2f} return (Effective rate: {effective_return_rate*100:.2f}%)."
            )

            cash_direct_from_return = current_grant_return / 2
            current_year_total_cash_to_employee += cash_direct_from_return
            year_cash_details["direct_from_returns"] += cash_direct_from_return
            year_cash_details["log"].append(
                f"    +${cash_direct_from_return:,.2f} paid as direct cash (50% of return)."
            )

            amount_for_second_half = current_grant_return / 2

            if not grant["payout_occurred"]:
                grant["accumulated_withheld"] += amount_for_second_half
                year_cash_details["log"].append(
                    f"    +${amount_for_second_half:,.2f} added to withheld. (Total withheld for G{grant['id']}: ${grant['accumulated_withheld']:,.2f})"
                )

                if grant["age_in_years"] == 5:
                    payout_amount = grant["accumulated_withheld"]
                    current_year_total_cash_to_employee += payout_amount
                    year_cash_details["payouts_from_withheld"] += payout_amount
                    year_cash_details["log"].append(
                        f"    PAYOUT! G{grant['id']} is 5 years old. Releasing withheld amount of ${payout_amount:,.2f}."
                    )
                    grant["accumulated_withheld"] = 0
                    grant["payout_occurred"] = True
            else:
                current_year_total_cash_to_employee += amount_for_second_half
                year_cash_details["direct_from_returns"] += amount_for_second_half  # Add to direct cash
                year_cash_details["log"].append(
                    f"    +${amount_for_second_half:,.2f} paid as cash (other 50% of return, post-payout period for G{grant['id']})."
                )

        # Calculate total withheld balance at the end of the year
        total_withheld_balance_end_of_year = sum(g["accumulated_withheld"] for g in active_grants)

        # Calculate total value of vested grants (grants that have been held for 5 years or more)
        total_vested_grants_value = sum(g["value"] for g in active_grants if g["age_in_years"] >= 5)

        yearly_cash_summary.append(
            {
                "year": current_sim_year,
                "total_cash_received": current_year_total_cash_to_employee,
                "total_withheld_balance_end_of_year": total_withheld_balance_end_of_year,
                "total_vested_grants_value": total_vested_grants_value,
                "details": year_cash_details,
            }
        )

        for log_entry in year_cash_details["log"]:
            print(log_entry)
        print(f"  Summary for Year {current_sim_year}:")
        print(f"    Cash from direct returns: ${year_cash_details['direct_from_returns']:,.2f}")
        print(f"    Cash from payouts of withheld amounts: ${year_cash_details['payouts_from_withheld']:,.2f}")
        print(f"  TOTAL CASH RECEIVED IN YEAR {current_sim_year}: ${current_year_total_cash_to_employee:,.2f}")
        print(f"  Total accumulated withheld balance (end of year): ${total_withheld_balance_end_of_year:,.2f}")
        print(f"  Total value of vested grants (5+ years): ${total_vested_grants_value:,.2f}\n")

    print("--- Overall Yearly Cash Summary ---")
    for entry in yearly_cash_summary:
        print(
            f"Year {entry['year']}: Total Cash Received = ${entry['total_cash_received']:,.2f}, End of Year Withheld Balance = ${entry['total_withheld_balance_end_of_year']:,.2f}, Vested Grants Value = ${entry['total_vested_grants_value']:,.2f}"
        )

    return yearly_cash_summary


if __name__ == "__main__":
    # --- Configuration ---
    annual_grant_value = 140000.00
    annual_return_rate = 0.07
    simulation_period_years = 20
    # New: Set decay rate. 0.0 means no decay. 0.01 means 1% decay of the rate per year.
    grant_return_decay = 0.01  # Example: 1% decay per year
    # --- End Configuration ---

    results = model_rsu_scheme(annual_grant_value, annual_return_rate, simulation_period_years, grant_return_decay)
