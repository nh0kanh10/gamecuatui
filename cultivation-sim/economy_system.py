"""
Dynamic Economy System
- Dynamic pricing based on supply/demand
- Vickrey Auction (second-price sealed bid)
- Price elasticity
- Economic cycles
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import random
import json
from pathlib import Path


class PriceElasticity(str, Enum):
    """Price elasticity types"""
    INELASTIC = "inelastic"  # Essential items (low elasticity)
    NORMAL = "normal"        # Normal items
    ELASTIC = "elastic"      # Luxury items (high elasticity)


class ItemPrice(BaseModel):
    """Dynamic price for an item"""
    item_id: str
    base_price: float = Field(gt=0, description="Base price")
    current_stock: int = Field(default=0, ge=0, description="Current stock")
    target_stock: int = Field(default=100, gt=0, description="Target stock level")
    elasticity: PriceElasticity = Field(default=PriceElasticity.NORMAL)
    price_multiplier: float = Field(default=1.0, gt=0, description="Current price multiplier")
    last_updated: datetime = Field(default_factory=datetime.now)


class AuctionBid(BaseModel):
    """Auction bid"""
    bidder_id: str
    item_id: str
    bid_amount: float = Field(gt=0)
    timestamp: datetime = Field(default_factory=datetime.now)
    is_sealed: bool = Field(default=True, description="Sealed bid (Vickrey)")


class VickreyAuction(BaseModel):
    """Vickrey Auction (second-price sealed bid)"""
    auction_id: str
    item_id: str
    item_name: str
    starting_price: float = Field(gt=0)
    bids: List[AuctionBid] = Field(default_factory=list)
    end_time: datetime
    is_active: bool = Field(default=True)
    
    def get_winner(self) -> Optional[Dict[str, Any]]:
        """Get auction winner (highest bidder pays second-highest price)"""
        if not self.bids:
            return None
        
        # Sort by bid amount (descending)
        sorted_bids = sorted(self.bids, key=lambda b: b.bid_amount, reverse=True)
        
        if len(sorted_bids) == 1:
            # Only one bidder, pays starting price
            return {
                "winner_id": sorted_bids[0].bidder_id,
                "winning_bid": sorted_bids[0].bid_amount,
                "price_paid": self.starting_price
            }
        
        # Winner pays second-highest price + small increment
        winner = sorted_bids[0]
        second_highest = sorted_bids[1].bid_amount
        price_paid = second_highest + (self.starting_price * 0.01)  # 1% increment
        
        return {
            "winner_id": winner.bidder_id,
            "winning_bid": winner.bid_amount,
            "price_paid": price_paid
        }


class EconomySystem:
    """
    Dynamic Economy System với dynamic pricing và auctions
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.item_prices: Dict[str, ItemPrice] = {}
        self.active_auctions: Dict[str, VickreyAuction] = {}
        self.economic_cycle: str = "normal"  # normal, prosperity, recession
        self.cycle_start_time: datetime = datetime.now()
        self.load_prices()
    
    def load_prices(self):
        """Load item prices from JSON"""
        prices_file = self.data_dir / "item_prices.json"
        if prices_file.exists():
            try:
                with open(prices_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item_data in data:
                        price = ItemPrice(**item_data)
                        self.item_prices[price.item_id] = price
            except Exception as e:
                print(f"❌ Error loading prices: {e}")
    
    def calculate_price(
        self,
        item_id: str,
        k: float = 1.5
    ) -> float:
        """
        Calculate dynamic price based on stock
        
        Formula: Price = BasePrice × (TargetStock / (CurrentStock + 1))^k
        
        Args:
            item_id: Item ID
            k: Price elasticity exponent (default 1.5)
        
        Returns:
            Current price
        """
        price_data = self.item_prices.get(item_id)
        if not price_data:
            return 0.0
        
        # Calculate price multiplier
        stock_ratio = price_data.target_stock / (price_data.current_stock + 1)
        price_multiplier = stock_ratio ** k
        
        # Apply elasticity modifier
        elasticity_modifier = self._get_elasticity_modifier(price_data.elasticity)
        price_multiplier *= elasticity_modifier
        
        # Apply economic cycle modifier
        cycle_modifier = self._get_cycle_modifier()
        price_multiplier *= cycle_modifier
        
        # Calculate final price
        final_price = price_data.base_price * price_multiplier
        
        # Update price data
        price_data.price_multiplier = price_multiplier
        price_data.last_updated = datetime.now()
        
        return max(0.01, final_price)  # Minimum price
    
    def _get_elasticity_modifier(self, elasticity: PriceElasticity) -> float:
        """Get price modifier based on elasticity"""
        if elasticity == PriceElasticity.INELASTIC:
            return 1.0  # Essential items, less price fluctuation
        elif elasticity == PriceElasticity.ELASTIC:
            return 1.2  # Luxury items, more price fluctuation
        else:
            return 1.0  # Normal
    
    def _get_cycle_modifier(self) -> float:
        """Get price modifier based on economic cycle"""
        if self.economic_cycle == "prosperity":
            return 1.1  # Prices increase
        elif self.economic_cycle == "recession":
            return 0.9  # Prices decrease
        else:
            return 1.0  # Normal
    
    def update_stock(self, item_id: str, delta: int):
        """Update item stock"""
        if item_id not in self.item_prices:
            return
        
        price_data = self.item_prices[item_id]
        price_data.current_stock = max(0, price_data.current_stock + delta)
        price_data.last_updated = datetime.now()
    
    def buy_item(
        self,
        item_id: str,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """
        Buy item at current price
        
        Returns:
            {"success": bool, "price": float, "total_cost": float, "quantity": int}
        """
        current_price = self.calculate_price(item_id)
        if current_price <= 0:
            return {"success": False, "error": "Item not found"}
        
        total_cost = current_price * quantity
        
        # Update stock (decrease when buying)
        self.update_stock(item_id, -quantity)
        
        return {
            "success": True,
            "item_id": item_id,
            "quantity": quantity,
            "unit_price": current_price,
            "total_cost": total_cost
        }
    
    def sell_item(
        self,
        item_id: str,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """
        Sell item at current price
        
        Returns:
            {"success": bool, "price": float, "total_revenue": float, "quantity": int}
        """
        current_price = self.calculate_price(item_id)
        if current_price <= 0:
            return {"success": False, "error": "Item not found"}
        
        # Selling price is usually lower (90% of buy price)
        sell_price = current_price * 0.9
        total_revenue = sell_price * quantity
        
        # Update stock (increase when selling)
        self.update_stock(item_id, quantity)
        
        return {
            "success": True,
            "item_id": item_id,
            "quantity": quantity,
            "unit_price": sell_price,
            "total_revenue": total_revenue
        }
    
    def create_auction(
        self,
        item_id: str,
        item_name: str,
        starting_price: float,
        duration_hours: int = 24
    ) -> str:
        """
        Create Vickrey auction
        
        Returns:
            Auction ID
        """
        import uuid
        auction_id = str(uuid.uuid4())
        
        auction = VickreyAuction(
            auction_id=auction_id,
            item_id=item_id,
            item_name=item_name,
            starting_price=starting_price,
            end_time=datetime.now() + timedelta(hours=duration_hours)
        )
        
        self.active_auctions[auction_id] = auction
        return auction_id
    
    def place_bid(
        self,
        auction_id: str,
        bidder_id: str,
        bid_amount: float
    ) -> Dict[str, Any]:
        """
        Place sealed bid in Vickrey auction
        
        Returns:
            {"success": bool, "message": str}
        """
        auction = self.active_auctions.get(auction_id)
        if not auction:
            return {"success": False, "error": "Auction not found"}
        
        if not auction.is_active:
            return {"success": False, "error": "Auction has ended"}
        
        if datetime.now() > auction.end_time:
            auction.is_active = False
            return {"success": False, "error": "Auction has ended"}
        
        if bid_amount < auction.starting_price:
            return {"success": False, "error": f"Bid must be at least {auction.starting_price}"}
        
        # Check if bidder already bid (update existing bid)
        existing_bid = next((b for b in auction.bids if b.bidder_id == bidder_id), None)
        if existing_bid:
            existing_bid.bid_amount = bid_amount
            existing_bid.timestamp = datetime.now()
        else:
            bid = AuctionBid(
                bidder_id=bidder_id,
                item_id=auction.item_id,
                bid_amount=bid_amount
            )
            auction.bids.append(bid)
        
        return {"success": True, "message": "Bid placed successfully"}
    
    def end_auction(self, auction_id: str) -> Optional[Dict[str, Any]]:
        """
        End auction and determine winner
        
        Returns:
            Winner info hoặc None
        """
        auction = self.active_auctions.get(auction_id)
        if not auction:
            return None
        
        auction.is_active = False
        winner = auction.get_winner()
        
        return winner
    
    def update_economic_cycle(self):
        """Update economic cycle (prosperity/recession)"""
        # Simple cycle: 30 days normal, 10 days prosperity, 10 days recession
        days_since_start = (datetime.now() - self.cycle_start_time).days
        cycle_day = days_since_start % 50
        
        if cycle_day < 30:
            self.economic_cycle = "normal"
        elif cycle_day < 40:
            self.economic_cycle = "prosperity"
        else:
            self.economic_cycle = "recession"
    
    def get_price_info(self, item_id: str) -> Dict[str, Any]:
        """Get price information for an item"""
        price_data = self.item_prices.get(item_id)
        if not price_data:
            return {}
        
        current_price = self.calculate_price(item_id)
        
        return {
            "item_id": item_id,
            "base_price": price_data.base_price,
            "current_price": current_price,
            "current_stock": price_data.current_stock,
            "target_stock": price_data.target_stock,
            "price_multiplier": price_data.price_multiplier,
            "elasticity": price_data.elasticity.value,
            "economic_cycle": self.economic_cycle
        }

