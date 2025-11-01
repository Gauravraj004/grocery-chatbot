import React, { useState } from 'react';

function ProductCard({ product }) {
  const [imgError, setImgError] = useState(false);
  const handleProductClick = () => {
    // Generate a search URL for the product
    const searchQuery = encodeURIComponent(`${product.name} ${product.vendor}`);
    const searchUrl = `https://www.google.com/search?q=${searchQuery}`;
    window.open(searchUrl, '_blank');
  };

  return (
    <div className="product-card" onClick={handleProductClick}>
      <div className="product-image-wrapper">
        {product.image && !imgError ? (
          <img
            src={product.image}
            alt={product.name}
            className="product-image"
            loading="lazy"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="image-fallback" aria-label="No image available">
            <span role="img" aria-hidden>🛒</span>
          </div>
        )}
      </div>
      <div className="product-info">
        <div className="product-name">{product.name}</div>
        <div className="product-details">
          <span className="product-price">£{product.price.toFixed(2)}</span>
          <span className="product-vendor">{product.vendor}</span>
        </div>
        {product.tags && product.tags.length > 0 && (
          <div className="product-tags">
            {product.tags.map((tag, index) => (
              <span key={index} className="product-tag">
                {tag}
              </span>
            ))}
          </div>
        )}
        {product.reason && (
          <div className="product-reason">
            💡 {product.reason}
          </div>
        )}
        {product.calories !== undefined && product.calories !== null && (
          <div style={{ fontSize: '0.7rem', color: '#666', marginTop: '0.3rem' }}>
            {product.calories === 0 ? '0 cal' : `${product.calories} cal`}
          </div>
        )}
      </div>
    </div>
  );
}

export default ProductCard;
