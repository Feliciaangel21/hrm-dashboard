import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.title("HRM Survey Dashboard")

uploaded_file = st.file_uploader("Upload the final HRM Excel file", type=["xlsx"])

# Use default if none uploaded
if uploaded_file is None:
    #st.warning("No file uploaded. Using sample data instead.")
    uploaded_file = "final_hrm_survey_output.xlsx"

if uploaded_file:
    # Load all sheets
    xls = pd.ExcelFile(uploaded_file)
    df = xls.parse("Cleaned Data")
    df_classified = xls.parse("Leaving Reasons") if "Leaving Reasons" in xls.sheet_names else None
    df_stay = xls.parse("Staying Reasons") if "Staying Reasons" in xls.sheet_names else None
    df_open = xls.parse("Raw Open Comments") if "Raw Open Comments" in xls.sheet_names else None

    # Summary insights
    st.header("Executive Summary")
    st.markdown("""
    This dashboard summarizes findings from an internal HRM survey conducted among employees across departments. The survey captured both structured (Likert scale) and open-ended responses, giving a well-rounded picture of employee sentiment.

### Key Findings:
- **Exit Intentions:** Most employees reported no serious intention of leaving; however, a non-negligible portion expressed mild to serious considerations. This signals a need to further investigate early signs of dissatisfaction.
- **Satisfaction Drivers:** Survey questions were rated on a 1–7 scale. Employees feel most confident in their understanding of their roles and their ability to express feedback, which shows a strong foundation in clarity and openness. On the lower end, career development and perceived advancement opportunities scored below average, which could be a red flag for future turnover.
- **Qualitative Insights:** Open-ended responses about reasons for leaving frequently mention infrastructure limitations, poor internal communication, and lack of recognition. On the flip side, reasons for staying commonly highlight cultural alignment, collegial support, and perceived mission integrity.
- **Thematic Analysis:** By semantically clustering open comments, we identified consistent patterns in employee sentiment that align with and reinforce quantitative trends.

Use this dashboard to interactively explore these trends and surface priority areas for HR action.
""")

    # Average satisfaction scores (filtered only for this section)
    st.subheader("Average Satisfaction Scores")
    if "exit_intention_encoded" in df.columns:
        if "exit_intention_encoded" in df.columns:
            exit_labels = {
            0: "Not at all",
            1: "Mild consideration",
            2: "Serious consideration"
        }
        df["exit_intention_label"] = df["exit_intention_encoded"].map(exit_labels)
        selected_exit = st.selectbox(
            "Filter Average Scores by Exit Intention",
            ["Not at all", "Mild consideration", "Serious consideration"]
        )
        df_filtered = df[df["exit_intention_label"] == selected_exit]
    else:
        df_filtered = df

    likert_cols = [col for col in df_filtered.columns if df_filtered[col].dtype in ['int64', 'float64'] and 'encoded' not in col]
    mean_scores = df_filtered[likert_cols].mean().sort_values()

    fig1, ax1 = plt.subplots(figsize=(8, 6))
    sns.barplot(x=mean_scores.values, y=mean_scores.index, palette='viridis', ax=ax1)
    ax1.set_title("Average Score per Survey Question")
    ax1.set_xlim(1, 7)
    st.pyplot(fig1)

    st.markdown("""
    **Interpretation:** Employees rated their understanding of roles, ability to give feedback, and internal motivation highly. These are strengths of the organization. However, lower scores in career development support and perceived advancement opportunities point to underlying dissatisfaction with long-term growth.
    """)

    # Exit intention encoded bar chart (summary view)
    if "exit_intention_encoded" in df.columns:
        exit_labels = {
            0: "Not at all",
            1: "Mild consideration",
            2: "Serious consideration"
        }
        df["exit_intention_label"] = df["exit_intention_encoded"].map(exit_labels)

        st.subheader("Exit Intention Summary (Encoded Responses)")
        exit_counts = df["exit_intention_label"].value_counts()
        fig_exit_summary, ax_exit_summary = plt.subplots(figsize=(6, 4))
        sns.barplot(x=exit_counts.index, y=exit_counts.values, palette="Reds", ax=ax_exit_summary)
        ax_exit_summary.set_xlabel("Exit Intention Level")
        ax_exit_summary.set_ylabel("Number of Employees")
        ax_exit_summary.set_title("Staff Who Considered Leaving")
        st.pyplot(fig_exit_summary)

    st.markdown("""
    **Interpretation:** While most employees do not currently intend to leave, the presence of serious exit intention among a minority suggests early signs of disengagement. Continuous monitoring is essential.
    """)

    # Exit intention raw chart
    st.subheader("Staff Who Considered Leaving")
    if "Apakah Anda pernah berpikir untuk meninggalkan yayasan ini dalam satu tahun terakhir?" in df.columns:
        fig_exit, ax_exit = plt.subplots(figsize=(6, 4))
        sns.countplot(y=df["Apakah Anda pernah berpikir untuk meninggalkan yayasan ini dalam satu tahun terakhir?"], palette="Reds", ax=ax_exit)
        ax_exit.set_title("Staff Who Considered Leaving (Past Year)")
        ax_exit.set_xlabel("Number of Respondents")
        ax_exit.set_ylabel("Response")
        st.pyplot(fig_exit)

    st.markdown("""
    **Insight:** When asked directly, a proportion of respondents did consider leaving within the past year. This emphasizes the importance of proactive retention efforts.
    """)

    # Leaving reasons
    if df_classified is not None:
        st.subheader("Most Common Issues Raised by Staff")
        theme_counts = df_classified["Predicted Theme"].value_counts()
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        sns.barplot(x=theme_counts.values, y=theme_counts.index, palette="Reds_r", ax=ax2)
        ax2.set_title("Top Issues Behind Exit Intentions")
        ax2.set_xlabel("Mentions")
        ax2.set_ylabel("Theme")
        st.pyplot(fig2)

        st.markdown("""
        **Insight:** Facilities and internal communication are the most frequent complaints. Leadership and recognition also feature significantly, echoing broader themes seen in both quantitative and qualitative data.
        """)

        selected_theme = st.selectbox("View Leaving Comments by Theme", theme_counts.index)
        unique_comments = df_classified[df_classified["Predicted Theme"] == selected_theme]["Reason"].drop_duplicates().head(10)
        for i, comment in enumerate(unique_comments, 1):
            st.markdown(f"**{i}.** {comment}")



    # Staying reasons
    if df_stay is not None:
        st.subheader("Top Reasons for Staying")
        stay_counts = df_stay["Predicted Theme"].value_counts()
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        sns.barplot(x=stay_counts.values, y=stay_counts.index, palette="Blues", ax=ax3)
        ax3.set_title("Auto-Classified Themes for Staying Reasons")
        st.pyplot(fig3)

        st.markdown("""
        **Insight:** Social belonging, mission alignment, and a positive work culture are primary motivators for employees to remain. These are protective factors worth reinforcing.
        """)

        selected_stay_theme = st.selectbox("View Staying Comments by Theme", stay_counts.index)
        unique_stay_comments = df_stay[df_stay["Predicted Theme"] == selected_stay_theme]["Reason"].drop_duplicates().head(10)
        for i, comment in enumerate(unique_stay_comments, 1):
            st.markdown(f"**{i}.** {comment}")


    # Most specific issues (open-ended)
    if df_open is not None and "problem_theme" in df_open.columns:
        st.subheader("Most Specific Issues Raised by Staff")
        issue_counts = df_open["problem_theme"].value_counts().sort_values(ascending=False)

        fig_issue, ax_issue = plt.subplots(figsize=(8, 5))
        sns.barplot(x=issue_counts.values, y=issue_counts.index, palette="rocket", ax=ax_issue)
        ax_issue.set_xlabel("Mentions")
        ax_issue.set_ylabel("Problem Theme")
        ax_issue.set_title("Most Specific Issues Raised by Staff")
        plt.tight_layout()
        st.pyplot(fig_issue)

        st.markdown("""
        **Insight:** Open-ended feedback highlights actionable problems such as communication gaps, physical work conditions, and leadership style. These granular issues provide a roadmap for tactical HR improvements.
        """)

        selected_issue_theme = st.selectbox("View Issue Comments by Theme", issue_counts.index)
        theme_comments = df_open[df_open["problem_theme"] == selected_issue_theme]["Suggested Improvements"].head(10)
        for i, comment in enumerate(theme_comments, 1):
            st.markdown(f"**{i}.** {comment}")


    # Correlation analysis
    st.header("Correlation Analysis Among Survey Items")
    if likert_cols:
        corr = df[likert_cols].corr()
        fig_corr, ax_corr = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax_corr)
        st.pyplot(fig_corr)
        st.markdown("""
        **Interpretation:**
        The correlation heatmap reveals several strong relationships:
        - *Perceived Career Opportunities* is highly correlated with *Career Planning Discussions* and *Career Development Support*.
        - *Motivation from Recognition* has a strong relationship with *Workplace Satisfaction*, indicating that recognition drives morale.
        - Low correlation for some items (like Training Support) suggests these may be weaker or more isolated drivers.
        """)
        st.markdown("""
        **Interpretation:** This heatmap shows how strongly each survey item correlates with others. Look for high positive values (>0.5) as indicators of related constructs (e.g., satisfaction and motivation).
        """)

    # Descriptive statistics summary
    st.header("Descriptive Statistics")
    desc_df = df[likert_cols].describe().transpose()
    st.dataframe(desc_df.style.format("{:.2f}"))
    st.markdown("""
    **Interpretation:**
    - *Understanding of Role & Goals* has the highest mean score, reflecting clarity in expectations.
    - *Training & Development Support* shows the lowest average and highest variance—highlighting a gap.
    - This disparity reveals an area for strategic HR development.
    """)

    # Cross-tab: Exit intention vs Tenure (if both exist)
    if "exit_intention_encoded" in df.columns and "Tenure" in df.columns:
        st.header("Cross-tabulation: Exit Intention vs Tenure")
        crosstab = pd.crosstab(df["Tenure"], df["exit_intention_label"])
        st.dataframe(crosstab)
        st.markdown("""
        **Interpretation:**
        - Employees with over 3 years tenure show high loyalty (more "Not at all").
        - Serious consideration to leave is more likely in early tenure.
        - Indicates onboarding and early retention should be prioritized.
        """)

    st.header("Conclusion and Recommendations")
    st.markdown("""
    Based on the analysis:
    - Focus HR efforts on improving perceived career growth opportunities and recognition.
    - Investigate specific issues raised around communication and infrastructure to design targeted interventions.
    - Continue strengthening positive culture and social support systems.

    Next steps include validating these findings via focus groups and reviewing exit interviews to triangulate the pain points raised.
    """)
else:
    st.info("Upload the final Excel file to begin.")
