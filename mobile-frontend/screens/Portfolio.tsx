import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, RefreshControl, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { LineChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';
import { Card } from '../components/Card';
import { PortfolioAsset } from '../types/portfolio';
import { fetchPortfolio, fetchPortfolioHistory } from '../services/api';
import { formatCurrency } from '../utils/formatters';
import { colors } from '../styles/colors';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';
import { PortfolioSummary } from '../components/PortfolioSummary';
import { AssetList } from '../components/AssetList';

const screenWidth = Dimensions.get('window').width;

const Portfolio = () => {
  const navigation = useNavigation();
  const [portfolio, setPortfolio] = useState<PortfolioAsset[]>([]);
  const [portfolioHistory, setPortfolioHistory] = useState({
    labels: ['', '', '', '', '', ''],
    datasets: [{ data: [0, 0, 0, 0, 0, 0] }]
  });
  const [totalValue, setTotalValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState('1W'); // '1D', '1W', '1M', '3M', '1Y', 'ALL'

  useEffect(() => {
    loadPortfolioData();
  }, [timeRange]);

  const loadPortfolioData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch portfolio assets
      const portfolioData = await fetchPortfolio();
      setPortfolio(portfolioData);
      
      // Calculate total portfolio value
      const total = portfolioData.reduce((sum, asset) => sum + asset.value, 0);
      setTotalValue(total);
      
      // Fetch portfolio history based on selected time range
      const historyData = await fetchPortfolioHistory(timeRange);
      setPortfolioHistory(historyData);
      
      setLoading(false);
    } catch (err) {
      console.error('Error loading portfolio data:', err);
      setError('Failed to load portfolio data. Please try again.');
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadPortfolioData();
    setRefreshing(false);
  };

  const handleAssetPress = (asset: PortfolioAsset) => {
    navigation.navigate('AssetDetails', { asset });
  };

  const handleAddAsset = () => {
    navigation.navigate('AddAsset');
  };

  const handleTimeRangeChange = (range: string) => {
    setTimeRange(range);
  };

  if (loading && !refreshing) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.title}>Portfolio</Text>
        <LoadingSpinner />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <View style={styles.header}>
          <Text style={styles.title}>Portfolio</Text>
          <TouchableOpacity 
            style={styles.addButton}
            onPress={handleAddAsset}
          >
            <Text style={styles.addButtonText}>+ Add Asset</Text>
          </TouchableOpacity>
        </View>

        {error ? (
          <ErrorMessage message={error} onRetry={loadPortfolioData} />
        ) : (
          <>
            <PortfolioSummary totalValue={totalValue} />

            <Card style={styles.chartCard}>
              <View style={styles.timeRangeSelector}>
                {['1D', '1W', '1M', '3M', '1Y', 'ALL'].map((range) => (
                  <TouchableOpacity
                    key={range}
                    style={[
                      styles.timeRangeButton,
                      timeRange === range && styles.timeRangeButtonActive
                    ]}
                    onPress={() => handleTimeRangeChange(range)}
                  >
                    <Text
                      style={[
                        styles.timeRangeText,
                        timeRange === range && styles.timeRangeTextActive
                      ]}
                    >
                      {range}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>

              <LineChart
                data={portfolioHistory}
                width={screenWidth - 40}
                height={220}
                chartConfig={{
                  backgroundColor: colors.cardBackground,
                  backgroundGradientFrom: colors.cardBackground,
                  backgroundGradientTo: colors.cardBackground,
                  decimalPlaces: 2,
                  color: (opacity = 1) => `rgba(46, 125, 50, ${opacity})`,
                  labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
                  style: {
                    borderRadius: 16
                  },
                  propsForDots: {
                    r: '6',
                    strokeWidth: '2',
                    stroke: colors.primary
                  }
                }}
                bezier
                style={styles.chart}
              />
            </Card>

            <View style={styles.assetsHeader}>
              <Text style={styles.assetsTitle}>Your Assets</Text>
              <TouchableOpacity onPress={() => navigation.navigate('AllAssets')}>
                <Text style={styles.viewAllText}>View All</Text>
              </TouchableOpacity>
            </View>

            <AssetList 
              assets={portfolio.slice(0, 5)} 
              onAssetPress={handleAssetPress} 
            />
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    padding: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: colors.text,
  },
  addButton: {
    backgroundColor: colors.primary,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
  },
  addButtonText: {
    color: colors.white,
    fontWeight: '600',
  },
  chartCard: {
    marginVertical: 16,
    padding: 16,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  timeRangeSelector: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  timeRangeButton: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  timeRangeButtonActive: {
    backgroundColor: colors.primaryLight,
  },
  timeRangeText: {
    color: colors.textSecondary,
    fontSize: 12,
  },
  timeRangeTextActive: {
    color: colors.primary,
    fontWeight: 'bold',
  },
  assetsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
    marginBottom: 12,
  },
  assetsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text,
  },
  viewAllText: {
    color: colors.primary,
    fontWeight: '600',
  },
});

export default Portfolio;
