"""
Reddit Data Fetcher for Sentiment Analysis.
Retrieves posts and comments from investment-related subreddits.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import praw

from app.data.fetchers.base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)


class RedditFetcher(BaseFetcher):
    """Fetcher for Reddit data via PRAW."""
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """
        Initialize Reddit fetcher.
        
        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        super().__init__(api_key=client_id)  # Use client_id as api_key for base class
        
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
    
    def _validate_credentials(self) -> None:
        """Validate Reddit API credentials."""
        if not self.client_id or not self.client_secret:
            raise ValueError("Reddit client_id and client_secret are required")
    
    def fetch(self, **kwargs) -> Dict[str, Any]:
        """Generic fetch method."""
        raise NotImplementedError("Use specific fetch methods")
    
    def fetch_subreddit_posts(
        self,
        subreddit_name: str,
        limit: int = 100,
        time_filter: str = "day",
        sort: str = "hot"
    ) -> Dict[str, Any]:
        """
        Fetch posts from a subreddit.
        
        Args:
            subreddit_name: Name of subreddit (e.g., 'wallstreetbets')
            limit: Maximum number of posts to fetch
            time_filter: Time filter ('hour', 'day', 'week', 'month', 'year', 'all')
            sort: Sort method ('hot', 'new', 'top', 'rising')
            
        Returns:
            List of posts with metadata
        """
        self._log_fetch("Reddit", {
            "subreddit": subreddit_name,
            "limit": limit,
            "sort": sort
        })
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get posts based on sort method
            if sort == "hot":
                posts = subreddit.hot(limit=limit)
            elif sort == "new":
                posts = subreddit.new(limit=limit)
            elif sort == "top":
                posts = subreddit.top(time_filter=time_filter, limit=limit)
            elif sort == "rising":
                posts = subreddit.rising(limit=limit)
            else:
                raise ValueError(f"Invalid sort method: {sort}")
            
            # Extract post data
            posts_data = []
            for post in posts:
                posts_data.append({
                    "id": post.id,
                    "title": post.title,
                    "selftext": post.selftext,
                    "author": str(post.author),
                    "created_utc": datetime.fromtimestamp(post.created_utc).isoformat(),
                    "score": post.score,
                    "upvote_ratio": post.upvote_ratio,
                    "num_comments": post.num_comments,
                    "url": post.url,
                    "permalink": f"https://reddit.com{post.permalink}"
                })
            
            data = {
                "subreddit": subreddit_name,
                "sort": sort,
                "time_filter": time_filter,
                "count": len(posts_data),
                "posts": posts_data
            }
            
            return self._success_response(data, "Reddit Posts")
            
        except Exception as e:
            return self._handle_error(e, "Reddit Posts")
    
    def fetch_ticker_mentions(
        self,
        ticker: str,
        subreddit_name: str = "wallstreetbets",
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Fetch posts mentioning a specific ticker.
        
        Args:
            ticker: Stock ticker symbol
            subreddit_name: Subreddit to search
            limit: Maximum number of results
            
        Returns:
            Posts mentioning the ticker
        """
        self._log_fetch("Reddit", {
            "ticker": ticker,
            "subreddit": subreddit_name,
            "type": "ticker_mentions"
        })
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Search for ticker mentions
            search_query = f"${ticker} OR {ticker}"
            posts = subreddit.search(search_query, limit=limit, time_filter="week")
            
            # Extract post data
            posts_data = []
            for post in posts:
                # Check if ticker is actually mentioned in title or body
                text = f"{post.title} {post.selftext}".upper()
                if ticker.upper() in text or f"${ticker.upper()}" in text:
                    posts_data.append({
                        "id": post.id,
                        "title": post.title,
                        "selftext": post.selftext[:500],  # Truncate long posts
                        "author": str(post.author),
                        "created_utc": datetime.fromtimestamp(post.created_utc).isoformat(),
                        "score": post.score,
                        "upvote_ratio": post.upvote_ratio,
                        "num_comments": post.num_comments,
                        "permalink": f"https://reddit.com{post.permalink}"
                    })
            
            data = {
                "ticker": ticker,
                "subreddit": subreddit_name,
                "count": len(posts_data),
                "posts": posts_data
            }
            
            return self._success_response(data, "Reddit Ticker Mentions")
            
        except Exception as e:
            return self._handle_error(e, "Reddit Ticker Mentions")
    
    def fetch_sentiment_snapshot(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch sentiment snapshot for a ticker from multiple subreddits.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Aggregated sentiment data
        """
        self._log_fetch("Reddit", {"ticker": ticker, "type": "sentiment_snapshot"})
        
        try:
            subreddits = ["wallstreetbets", "stocks", "investing"]
            all_mentions = []
            
            for sub in subreddits:
                try:
                    result = self.fetch_ticker_mentions(ticker, sub, limit=50)
                    if result["success"]:
                        all_mentions.extend(result["data"]["posts"])
                except Exception as e:
                    logger.warning(f"Failed to fetch from r/{sub}: {e}")
            
            # Calculate basic sentiment metrics
            total_mentions = len(all_mentions)
            total_score = sum(post["score"] for post in all_mentions)
            avg_score = total_score / total_mentions if total_mentions > 0 else 0
            avg_upvote_ratio = sum(post["upvote_ratio"] for post in all_mentions) / total_mentions if total_mentions > 0 else 0
            
            data = {
                "ticker": ticker,
                "total_mentions": total_mentions,
                "average_score": avg_score,
                "average_upvote_ratio": avg_upvote_ratio,
                "subreddits_searched": subreddits,
                "recent_posts": all_mentions[:10]  # Top 10 most recent
            }
            
            return self._success_response(data, "Reddit Sentiment Snapshot")
            
        except Exception as e:
            return self._handle_error(e, "Reddit Sentiment Snapshot")


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "FynRAG/1.0")
    
    if not client_id or not client_secret:
        print("Reddit credentials not found in environment")
        exit(1)
    
    fetcher = RedditFetcher(client_id, client_secret, user_agent)
    
    ticker = "AAPL"
    print(f"\nFetching Reddit sentiment for {ticker}...")
    
    sentiment = fetcher.fetch_sentiment_snapshot(ticker)
    
    if sentiment["success"]:
        data = sentiment["data"]
        print(f"\nTotal mentions: {data['total_mentions']}")
        print(f"Average score: {data['average_score']:.2f}")
        print(f"Average upvote ratio: {data['average_upvote_ratio']:.2%}")
