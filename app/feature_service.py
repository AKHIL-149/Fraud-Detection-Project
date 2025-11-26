"""
Feature Service Module
Real-time feature computation for incoming transactions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

class FeatureService:
    """
    Computes features for real-time fraud detection.
    Maintains in-memory state for velocity and behavioral features.
    """

    def __init__(self):
        # In-memory storage for transaction history
        self.transaction_history = defaultdict(list)
        self.user_profiles = {}
        self.merchant_stats = {}

    def compute_features(self, transaction):
        """
        Compute all features for a single transaction.

        Args:
            transaction: Dictionary with transaction details

        Returns:
            Dictionary with computed features
        """
        features = {}

        # Extract basic fields
        user_id = transaction.get('User', 0)
        card_id = transaction.get('Card', 0)
        amount = float(transaction.get('Amount', 0))
        timestamp = transaction.get('DateTime', datetime.now())

        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp)

        # Temporal features
        features.update(self._compute_temporal_features(timestamp))

        # Amount features
        features.update(self._compute_amount_features(amount, user_id, transaction))

        # Velocity features
        features.update(self._compute_velocity_features(user_id, card_id, timestamp, amount))

        # Merchant features
        features.update(self._compute_merchant_features(transaction, user_id))

        # Geographic features
        features.update(self._compute_geographic_features(transaction))

        # User behavior features
        features.update(self._compute_user_features(user_id))

        # Card features
        features.update(self._compute_card_features(transaction))

        # Store transaction in history
        self._update_transaction_history(user_id, card_id, timestamp, amount, transaction)

        return features

    def _compute_temporal_features(self, timestamp):
        """Compute time-based features"""
        hour = timestamp.hour
        # Use weekday() for datetime objects (0=Monday), dayofweek for pandas Timestamp
        day_of_week = timestamp.weekday() if hasattr(timestamp, 'weekday') else timestamp.dayofweek

        return {
            'hour': hour,
            'day_of_week': day_of_week,
            'day_of_month': timestamp.day,
            'month': timestamp.month,
            'year': timestamp.year,
            'is_weekend': 1 if day_of_week >= 5 else 0,
            'hour_sin': np.sin(2 * np.pi * hour / 24),
            'hour_cos': np.cos(2 * np.pi * hour / 24),
            'dow_sin': np.sin(2 * np.pi * day_of_week / 7),
            'dow_cos': np.cos(2 * np.pi * day_of_week / 7)
        }

    def _compute_amount_features(self, amount, user_id, transaction):
        """Compute amount-related features"""
        features = {
            'amount_log': np.log1p(amount),
            'is_round_amount': 1 if amount % 10 == 0 and amount > 0 else 0,
            'is_refund': 1 if amount < 0 else 0
        }

        # Deviation from user average
        if user_id in self.user_profiles:
            user_avg = self.user_profiles[user_id].get('avg_amount', amount)
            user_std = self.user_profiles[user_id].get('std_amount', 1)
            features['amount_vs_user_avg'] = (amount - user_avg) / (user_std + 1)
        else:
            features['amount_vs_user_avg'] = 0

        # Merchant category deviation
        mcc = transaction.get('MCC', 0)
        if mcc in self.merchant_stats:
            mcc_avg = self.merchant_stats[mcc].get('avg_amount', amount)
            mcc_std = self.merchant_stats[mcc].get('std_amount', 1)
            features['amount_vs_mcc_avg'] = (amount - mcc_avg) / (mcc_std + 1)
        else:
            features['amount_vs_mcc_avg'] = 0

        return features

    def _compute_velocity_features(self, user_id, card_id, timestamp, amount):
        """Compute transaction velocity features"""
        key = f"{user_id}_{card_id}"
        history = self.transaction_history.get(key, [])

        if not history:
            return {
                'time_since_last_txn': 86400,  # Default 24 hours
                'txn_count_1h': 1,
                'txn_count_24h': 1,
                'txn_count_7d': 1,
                'amount_sum_24h': amount
            }

        # Time since last transaction
        last_txn = history[-1] if history else None
        time_since_last = (timestamp - last_txn['timestamp']).total_seconds() if last_txn else 86400

        # Count transactions in time windows
        one_hour_ago = timestamp - timedelta(hours=1)
        one_day_ago = timestamp - timedelta(days=1)
        seven_days_ago = timestamp - timedelta(days=7)

        txn_count_1h = sum(1 for txn in history if txn['timestamp'] >= one_hour_ago)
        txn_count_24h = sum(1 for txn in history if txn['timestamp'] >= one_day_ago)
        txn_count_7d = sum(1 for txn in history if txn['timestamp'] >= seven_days_ago)

        # Amount sum in last 24 hours
        amount_sum_24h = sum(txn['amount'] for txn in history if txn['timestamp'] >= one_day_ago)

        return {
            'time_since_last_txn': time_since_last,
            'txn_count_1h': txn_count_1h + 1,  # Include current transaction
            'txn_count_24h': txn_count_24h + 1,
            'txn_count_7d': txn_count_7d + 1,
            'amount_sum_24h': amount_sum_24h + amount
        }

    def _compute_merchant_features(self, transaction, user_id):
        """Compute merchant-related features"""
        merchant_name = transaction.get('Merchant Name', 0)
        merchant_city = transaction.get('Merchant City', '')
        use_chip = transaction.get('Use Chip', 'Swipe Transaction')
        mcc = transaction.get('MCC', 0)

        features = {
            'is_online': 1 if merchant_city == 'ONLINE' else 0,
            'is_chip_txn': 1 if 'Chip' in use_chip else 0,
            'is_swipe_txn': 1 if 'Swipe' in use_chip else 0,
            'is_online_txn': 1 if 'Online' in use_chip else 0,
            'merchant_txn_count': self.merchant_stats.get(merchant_name, {}).get('count', 1),
            'mcc_frequency': self.merchant_stats.get(mcc, {}).get('frequency', 1)
        }

        # First time with merchant
        user_key = f"{user_id}_{merchant_name}"
        features['is_first_merchant_txn'] = 1 if user_key not in self.user_profiles else 0
        features['user_merchant_txn_count'] = self.user_profiles.get(user_key, {}).get('count', 0)

        return features

    def _compute_geographic_features(self, transaction):
        """Compute location-based features"""
        state = transaction.get('Merchant State', '')

        high_risk_states = ['Italy', 'OH']
        primary_states = ['CA', 'NY']
        international_states = ['Mexico', 'Italy', 'Poland', 'Philippines', 'Peru',
                               'Pakistan', 'China', 'Japan', 'Canada', 'UK']

        return {
            'is_international': 1 if state in international_states else 0,
            'is_high_risk_state': 1 if state in high_risk_states else 0,
            'is_primary_state': 1 if state in primary_states else 0,
            'missing_geo_data': 1 if not state or pd.isna(state) else 0,
            'state_txn_count': self.merchant_stats.get(f"state_{state}", {}).get('count', 1)
        }

    def _compute_user_features(self, user_id):
        """Compute user behavior features"""
        profile = self.user_profiles.get(user_id, {})

        return {
            'user_card_count': profile.get('card_count', 1),
            'user_merchant_diversity': profile.get('merchant_diversity', 1),
            'user_mcc_diversity': profile.get('mcc_diversity', 1),
            'user_avg_amount': profile.get('avg_amount', 50),
            'user_txn_per_day': profile.get('txn_per_day', 1)
        }

    def _compute_card_features(self, transaction):
        """Compute card-related features"""
        card_id = transaction.get('Card', 0)

        # Placeholder values - in production, fetch from card database
        return {
            'card_txn_count': 1,
            'card_on_dark_web': 0,
            'card_has_chip': 1,
            'chip_mismatch': 0,
            'is_visa': 1,
            'is_mastercard': 0,
            'is_debit': 1,
            'is_credit': 0
        }

    def _update_transaction_history(self, user_id, card_id, timestamp, amount, transaction):
        """Store transaction in history for velocity calculations"""
        key = f"{user_id}_{card_id}"

        txn_record = {
            'timestamp': timestamp,
            'amount': amount,
            'merchant': transaction.get('Merchant Name', 0),
            'mcc': transaction.get('MCC', 0)
        }

        self.transaction_history[key].append(txn_record)

        # Keep only last 7 days of history
        seven_days_ago = timestamp - timedelta(days=7)
        self.transaction_history[key] = [
            txn for txn in self.transaction_history[key]
            if txn['timestamp'] >= seven_days_ago
        ]

        # Update user profile
        self._update_user_profile(user_id, amount, transaction)

    def _update_user_profile(self, user_id, amount, transaction):
        """Update user behavioral profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'avg_amount': amount,
                'std_amount': 0,
                'card_count': 1,
                'merchant_diversity': 1,
                'mcc_diversity': 1,
                'txn_count': 1,
                'txn_per_day': 1
            }
        else:
            profile = self.user_profiles[user_id]
            profile['txn_count'] += 1
            # Update running average
            profile['avg_amount'] = (profile['avg_amount'] * (profile['txn_count'] - 1) + amount) / profile['txn_count']


# Global feature service instance
feature_service = FeatureService()
