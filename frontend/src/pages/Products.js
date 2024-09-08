import React, {useState, useEffect} from 'react';
import {useNavigate} from 'react-router-dom';
import axios from 'axios';
import Layout from '../components/Layout';

const Products = () => {
    const [products, setProducts] = useState([]);
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [filters, setFilters] = useState({
        condition: '',
        gender: '',
        brand: '',
        sortBy: 'title',
        order: 'asc',
    });
    const [filterOptions, setFilterOptions] = useState({
        conditions: [],
        genders: [],
        brands: [],
    });
    const navigate = useNavigate();

    const fetchProducts = async (page = 1) => {
        try {
            const response = await axios.get(`${process.env.REACT_APP_API_URL}/list-products/`, {
                headers: {Authorization: `Token ${localStorage.getItem('token')}`},
                params: {
                    page: page,
                    condition: filters.condition !== 'All Conditions' ? filters.condition : '',
                    gender: filters.gender !== 'All Genders' ? filters.gender : '',
                    brand: filters.brand !== 'All Brands' ? filters.brand : '',
                    sort_by: filters.sortBy,
                    order: filters.order,
                },
            });
            setProducts(response.data.results);
            setTotalPages(response.data.total_pages);
        } catch (error) {
            console.error('Failed to fetch products:', error);
        }
    };

    const fetchFilterOptions = async () => {
        try {
            const response = await axios.get(`${process.env.REACT_APP_API_URL}/filter-options/`, {
                headers: {Authorization: `Token ${localStorage.getItem('token')}`},
            });
            setFilterOptions({
                conditions: ['All Conditions', ...response.data.conditions],
                genders: ['All Genders', ...response.data.genders],
                brands: ['All Brands', ...response.data.brands],
            });
        } catch (error) {
            console.error('Failed to fetch filter options:', error);
        }
    };

    useEffect(() => {
        if (!localStorage.getItem('token')) {
            navigate('/signin');
        } else {
            fetchFilterOptions();
            fetchProducts(page);
        }
    }, [page, filters]);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('file', file);

        try {
            await axios.post(`${process.env.REACT_APP_API_URL}/upload-products/`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    Authorization: `Token ${localStorage.getItem('token')}`,
                },
            });
            setMessage('Products uploaded successfully!');
            await fetchProducts();
            await fetchFilterOptions();
        } catch (error) {
            setError('Upload failed');
            console.error('Upload error:', error);
        }
    };

    const handlePageChange = (newPage) => {
        setPage(newPage);
    };

    const handleFilterChange = (e) => {
        setFilters({
            ...filters,
            [e.target.name]: e.target.value,
        });
    };

    const isFiltering = () => {
        return (
            filters.condition !== 'All Conditions' ||
            filters.gender !== 'All Genders' ||
            filters.brand !== 'All Brands'
        );
    };

    return (
        <Layout>
            <div>
                <div className="upload-section filter-section">
                    <h2>Upload Products</h2>
                    <form onSubmit={handleUpload}>
                        <input type="file" onChange={handleFileChange}/>
                        <button type="submit">Upload</button>
                    </form>
                    {message && <p>{message}</p>}
                    {error && <p>{error}</p>}

                    {/* Show filter section if products are available or a filter is applied */}
                    {(products.length > 0 || isFiltering()) && (
                        <>
                            <h2>Filter Products</h2>
                            <form>
                                <select name="condition" value={filters.condition} onChange={handleFilterChange}>
                                    {filterOptions.conditions.map((condition) => (
                                        <option key={condition} value={condition}>
                                            {condition}
                                        </option>
                                    ))}
                                </select>
                                <select name="gender" value={filters.gender} onChange={handleFilterChange}>
                                    {filterOptions.genders.map((gender) => (
                                        <option key={gender} value={gender}>
                                            {gender}
                                        </option>
                                    ))}
                                </select>
                                <select name="brand" value={filters.brand} onChange={handleFilterChange}>
                                    {filterOptions.brands.map((brand) => (
                                        <option key={brand} value={brand}>
                                            {brand}
                                        </option>
                                    ))}
                                </select>
                                <select name="sortBy" value={filters.sortBy} onChange={handleFilterChange}>
                                    <option value="title">Title</option>
                                    <option value="price">Price</option>
                                </select>
                                <select name="order" value={filters.order} onChange={handleFilterChange}>
                                    <option value="asc">Asc</option>
                                    <option value="desc">Desc</option>
                                </select>
                            </form>
                        </>
                    )}
                </div>

                <div className="list-section">
                    {/* Show "No products available" if filtering but no products are found */}
                    {products.length === 0 && isFiltering() ? (
                        <p>No products available</p>
                    ) : products.length > 0 ? (
                        <>
                            <h2>Product List</h2>
                            <div className="table-wrapper">
                                <table>
                                    <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Image Link</th>
                                        <th>Title</th>
                                        <th>Product Type</th>
                                        <th>Brand</th>
                                        <th>Link</th>
                                        <th>Price</th>
                                        <th>Sale Price</th>
                                        <th>Old Price</th>
                                        <th>Final Price</th>
                                        <th>Availability</th>
                                        <th>Color</th>
                                        <th>Gender</th>
                                        <th>Quantity</th>
                                        <th>Condition</th>
                                        <th>Age Group</th>
                                        <th>Description</th>
                                        <th>Google Product Category</th>
                                        <th>GTIN</th>
                                        <th>Item Group ID</th>
                                        <th>Custom Label 0</th>
                                        <th>Custom Label 1</th>
                                        <th>Custom Label 2</th>
                                        <th>Custom Label 3</th>
                                        <th>Custom Label 4</th>
                                        <th>iPhone App Name</th>
                                        <th>iPhone App Store ID</th>
                                        <th>iPhone URL</th>
                                        <th>Discount Percent</th>
                                        <th>Gender Original Value</th>
                                        <th>Adult</th>
                                        <th>Adwords Labels</th>
                                        <th>Additional Images Count</th>
                                        <th>iOS URL</th>
                                        <th>iOS App Store ID</th>
                                        <th>iOS App Name</th>
                                        <th>Android Package</th>
                                        <th>Android App Name</th>
                                        <th>Options Percentage</th>
                                        <th>Icon Media URL</th>
                                        <th>All Sizes SKUs</th>
                                        <th>Sizes of All SKUs</th>
                                        <th>Product Season</th>
                                        <th>Product Class</th>
                                    </tr>
                                    </thead>
                                    <tbody>
                                    {products.map((product) => (
                                        <tr key={product.id}>
                                            <td>{product.id}</td>
                                            <td>
                                                <a href={product.image_link} target="_blank" rel="noopener noreferrer">
                                                    <img src={product.image_link} alt={product.title} style={{width: '100px', height: '100px'}}/>
                                                </a>
                                            </td>
                                            <td>{product.title}</td>
                                            <td>{product.product_type}</td>
                                            <td>{product.brand}</td>
                                            <td><a href={product.link} target="_blank" rel="noopener noreferrer">View</a></td>
                                            <td>{product.price}</td>
                                            <td>{product.sale_price}</td>
                                            <th>{product.old_price}</th>
                                            <td>{product.final_price}</td>
                                            <td>{product.availability}</td>
                                            <td>{product.color}</td>
                                            <td>{product.gender}</td>
                                            <td>{product.quantity}</td>
                                            <td>{product.condition}</td>
                                            <td>{product.age_group}</td>
                                            <td className="description">
                                                <div
                                                    dangerouslySetInnerHTML={{
                                                        __html: product.description.replace(/\. /g, '.<br />')
                                                    }}
                                                />
                                            </td>
                                            <td>{product.google_product_category}</td>
                                            <td>{product.gtin}</td>
                                            <td>{product.item_group_id}</td>
                                            <td>{product.custom_label_0}</td>
                                            <td>{product.custom_label_1}</td>
                                            <td>{product.custom_label_2}</td>
                                            <td>{product.custom_label_3}</td>
                                            <td>{product.custom_label_4}</td>
                                            <td>{product.iphone_app_name}</td>
                                            <td>{product.iphone_app_store_id}</td>
                                            <td>{product.iphone_url}</td>
                                            <td>{product.discount_percent}</td>
                                            <td>{product.gender_orig_value}</td>
                                            <td>{product.adult}</td>
                                            <td>{product.adwords_labels}</td>
                                            <td>{product.additional_images_count}</td>
                                            <td>{product.ios_url}</td>
                                            <td>{product.ios_app_store_id}</td>
                                            <td>{product.ios_app_name}</td>
                                            <td>{product.android_package}</td>
                                            <td>{product.android_app_name}</td>
                                            <td>{product.options_percentage}</td>
                                            <td>{product.icon_media_url}</td>
                                            <td>{product.all_sizes_skus}</td>
                                            <td>{product.sizes_of_all_skus}</td>
                                            <td>{product.product_season}</td>
                                            <td>{product.product_class}</td>
                                        </tr>
                                    ))}
                                    </tbody>
                                </table>
                            </div>
                        </>
                    ) : (
                        !isFiltering() && <p>No products available</p>
                    )}

                    {/* Only show pagination if we have products */}
                    {products.length > 0 && (
                        <div className="pagination">
                            {Array.from({length: totalPages}, (_, i) => (
                                <button key={i} onClick={() => handlePageChange(i + 1)} disabled={i + 1 === page}>
                                    {i + 1}
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </Layout>
    );
};

export default Products;
