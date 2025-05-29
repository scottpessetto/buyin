import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from buyin import model_rsu_scheme

# Set page title and configuration
st.set_page_config(page_title="RSU Scheme Simulator", layout="wide")
st.title("RSU Scheme Simulator")

st.write(
    """
This application simulates an RSU (Restricted Stock Unit) scheme over a number of years.
You can adjust the parameters using the sliders on the left and see how they affect the cash received 
and withheld balance.
"""
)

# Sidebar for inputs
st.sidebar.header("Input Parameters")

grant_size = st.sidebar.number_input(
    "Annual Grant Size ($)", min_value=10000.0, max_value=1000000.0, value=55000.0, step=10000.0, format="%.2f"
)

annual_return_percentage = (
    st.sidebar.slider("Annual Return Rate (%)", min_value=0.0, max_value=30.0, value=10.0, step=0.5) / 100
)  # Convert percentage to decimal

simulation_years = st.sidebar.slider("Simulation Period (Years)", min_value=5, max_value=30, value=10, step=1)

return_decay_rate_per_year = (
    st.sidebar.slider("Return Decay Rate Per Year (%)", min_value=0.0, max_value=10.0, value=0.0, step=0.1) / 100
)  # Convert percentage to decimal

# Run simulation when user clicks the button
if st.sidebar.button("Run Simulation"):
    # Run the model with the selected parameters
    results = model_rsu_scheme(grant_size, annual_return_percentage, simulation_years, return_decay_rate_per_year)

    # Convert results to DataFrame for easier display and plotting
    df_results = pd.DataFrame(
        [
            {
                "Year": entry["year"],
                "Cash Received ($)": entry["total_cash_received"],
                "Withheld Balance ($)": entry["total_withheld_balance_end_of_year"],
                "Vested Grants Value ($)": entry["total_vested_grants_value"],
            }
            for entry in results
        ]
    )

    # Display results in a table
    st.subheader("Yearly Results")
    st.dataframe(
        df_results.style.format(
            {"Cash Received ($)": "${:,.2f}", "Withheld Balance ($)": "${:,.2f}", "Vested Grants Value ($)": "${:,.2f}"}
        )
    )

    # Create a bar chart for Cash Received and Withheld Balance
    st.subheader("Cash Received vs Withheld Balance")

    fig1, ax1 = plt.subplots(figsize=(12, 6))

    # Set the style
    sns.set_style("whitegrid")

    # Create the bar chart
    x = df_results["Year"]
    width = 0.35

    # Plot bars
    ax1.bar(x - width / 2, df_results["Cash Received ($)"], width, label="Cash Received")
    ax1.bar(x + width / 2, df_results["Withheld Balance ($)"], width, label="Withheld Balance")

    # Add labels and title
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Amount ($)")
    ax1.set_title("Cash Received vs Withheld Balance Over Time")
    ax1.legend()

    # Format y-axis to show dollar amounts
    import matplotlib.ticker as mtick

    ax1.yaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.0f}"))

    # Rotate x-axis labels for better readability if needed
    plt.xticks(rotation=0)

    # Display the chart
    st.pyplot(fig1)

    # Create a separate bar chart for Vested Grants Value
    st.subheader("Total Value of Vested Grants")

    fig2, ax2 = plt.subplots(figsize=(12, 6))

    # Plot bars for vested grants
    ax2.bar(x, df_results["Vested Grants Value ($)"], width, color="green", label="Vested Grants Value")

    # Add labels and title
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Amount ($)")
    ax2.set_title("Total Value of Vested Grants Over Time")
    ax2.legend()

    # Format y-axis to show dollar amounts
    ax2.yaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.0f}"))

    # Display the chart
    st.pyplot(fig2)

    # Additional visualization - Line chart showing cumulative cash received
    st.subheader("Cumulative Cash Received Over Time")

    df_results["Cumulative Cash Received ($)"] = df_results["Cash Received ($)"].cumsum()

    fig3, ax3 = plt.subplots(figsize=(12, 6))
    sns.lineplot(x="Year", y="Cumulative Cash Received ($)", data=df_results, marker="o", linewidth=2, ax=ax3)
    ax3.set_xlabel("Year")
    ax3.set_ylabel("Cumulative Amount ($)")
    ax3.set_title("Cumulative Cash Received Over Time")
    ax3.yaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.0f}"))

    st.pyplot(fig3)

    # Display detailed breakdown for each year
    st.subheader("Detailed Breakdown")

    for entry in results:
        with st.expander(f"Year {entry['year']} Details"):
            st.write(f"**Cash from direct returns:** ${entry['details']['direct_from_returns']:,.2f}")
            st.write(f"**Cash from payouts of withheld amounts:** ${entry['details']['payouts_from_withheld']:,.2f}")
            st.write(f"**Total cash received:** ${entry['total_cash_received']:,.2f}")
            st.write(f"**End of year withheld balance:** ${entry['total_withheld_balance_end_of_year']:,.2f}")
            st.write(f"**Total value of vested grants (5+ years):** ${entry['total_vested_grants_value']:,.2f}")

            st.write("**Detailed log:**")
            for log_entry in entry["details"]["log"]:
                st.write(log_entry)
else:
    st.info("Adjust the parameters on the sidebar and click 'Run Simulation' to see the results.")
