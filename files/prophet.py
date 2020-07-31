import altair as alt
import matplotlib
import pandas as pd
from fbprophet import Prophet
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()

matplotlib.style.use('ggplot')

def fit_predict_model(dataframe, interval_width=0.85, changepoint_range=0.95):
    """Create the model used by prophet to detect anomalies
       Inspired by https://towardsdatascience.com/anomaly-detection-time-series-4c661f6f165f"""
    m = Prophet(daily_seasonality=False, yearly_seasonality=False, weekly_seasonality=False,
                interval_width=interval_width,
                changepoint_range=changepoint_range)
    m = m.fit(dataframe)
    forecast = m.predict(dataframe)
    forecast['fact'] = dataframe['y'].reset_index(drop=True)
    return forecast

def detect_anomalies(forecast):
    """Detect anomalies in the forecast realized by Prophet
       Copied from https://towardsdatascience.com/anomaly-detection-time-series-4c661f6f165f"""
    forecasted = forecast[['ds', 'trend', 'yhat', 'yhat_lower', 'yhat_upper', 'fact']].copy()

    forecasted['anomaly'] = 0
    forecasted.loc[forecasted['fact'] > forecasted['yhat_upper'], 'anomaly'] = 1
    forecasted.loc[forecasted['fact'] < forecasted['yhat_lower'], 'anomaly'] = -1

    # anomaly importances
    forecasted['importance'] = 0
    forecasted.loc[forecasted['anomaly'] == 1, 'importance'] = \
        (forecasted['fact'] - forecasted['yhat_upper']) / forecast['fact']
    forecasted.loc[forecasted['anomaly'] == -1, 'importance'] = \
        (forecasted['yhat_lower'] - forecasted['fact']) / forecast['fact']

    return forecasted

def plot_anomalies(forecasted):
    """Show plot with anomalies
       Inspired from https://towardsdatascience.com/anomaly-detection-time-series-4c661f6f165f"""
    interval = alt.Chart(forecasted).mark_area(interpolate="basis", color='#adadad').encode(
        x=alt.X('ds:T', title='Time'),
        y='yhat_upper',
        y2='yhat_lower',
        tooltip=['ds', 'fact', 'yhat_lower', 'yhat_upper']
    ).interactive().properties(
        title='Anomaly Detection'
    )

    fact = alt.Chart(forecasted[forecasted.anomaly == 0]).mark_circle(size=15, opacity=0.7, color='Black').encode(
        x='ds:T',
        y=alt.Y('fact', title='CPU Utilization [%]'),
        tooltip=['ds', 'fact', 'yhat_lower', 'yhat_upper']
    ).interactive()

    anomalies = alt.Chart(forecasted[forecasted.anomaly != 0]).mark_circle(size=30, color='Red').encode(
        x='ds:T',
        y=alt.Y('fact', title='CPU Utilization [%]'),
        tooltip=['ds', 'fact', 'yhat_lower', 'yhat_upper'],
        size=alt.Size('importance', legend=None)
    ).interactive()

    return alt.layer(interval, fact, anomalies) \
        .properties(width=870, height=450) \
        .configure_title(fontSize=20)


alt.renderers.enable('altair_viewer')

if __name__ == '__main__':
    # a = AnalyseLogs()

    # Dataframe used by the Prophet library
    df = pd.read_csv('test_data_cpu.csv', parse_dates=['ds'])
    df_sorted = df.sort_values(by=['ds'])
    df_sorted['y'] = df['y'].apply(lambda x: x * 100 / 4)

    # Analyze the time series with Prophet model, and show the results
    forecast = fit_predict_model(df_sorted)
    forecasted = detect_anomalies(forecast)
    fig1 = plot_anomalies(forecasted)
    fig1.show()
