import React, {useState, useEffect} from 'react';
import {useNavigate} from 'react-router-dom';
import axios from 'axios';
import Layout from './Layout';

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
                    condition: filters.condition !== 'All' ? filters.condition : '',
                    gender: filters.gender !== 'All' ? filters.gender : '',
                    brand: filters.brand !== 'All' ? filters.brand : '',
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
                conditions: ['All', ...response.data.conditions],
                genders: ['All', ...response.data.genders],
                brands: ['All', ...response.data.brands],
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
                </div>

                <div className="list-section">
                    <h2>Product List</h2>
                    {products.length === 0 ? (
                        <p>No products available</p>
                    ) : (
                        <div className="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Product Type</th>
                        <th>Link</th>
                        <th>Description</th>
                        <th>Image Link</th>
                        <th>Price</th>
                        <th>Final Price</th>
                        <th>Availability</th>
                        <th>Google Product Category</th>
                        <th>Brand</th>
                        <th>GTIN</th>
                        <th>Item Group ID</th>
                        <th>Condition</th>
                        <th>Age Group</th>
                        <th>Color</th>
                        <th>Gender</th>
                        <th>Quantity</th>
                        <th>Custom Label 0</th>
                        <th>Custom Label 1</th>
                        <th>Custom Label 2</th>
                        <th>Custom Label 3</th>
                        <th>Custom Label 4</th>
                    </tr>
                </thead>
                <tbody>
                    {products.map((product) => (
                        <tr key={product.id}>
                            <td>{product.id}</td>
                            <td>{product.title}</td>
                            <td>{product.product_type}</td>
                            <td><a href={product.link} target="_blank" rel="noopener noreferrer">View</a></td>
                            <td className="description" dangerouslySetInnerHTML={{ __html: product.description }} />
                            <td>
                                <a href={product.image_link} target="_blank" rel="noopener noreferrer">
                                    <img src={product.image_link} alt={product.title} style={{ width: '100px', height: '100px' }} />
                                </a>
                            </td>
                            <td>{product.price}</td>
                            <td>{product.finalprice}</td>
                            <td>{product.availability}</td>
                            <td>{product.google_product_category}</td>
                            <td>{product.brand}</td>
                            <td>{product.gtin}</td>
                            <td>{product.item_group_id}</td>
                            <td>{product.condition}</td>
                            <td>{product.age_group}</td>
                            <td>{product.color}</td>
                            <td>{product.gender}</td>
                            <td>{product.quantity}</td>
                            <td>{product.custom_label_0}</td>
                            <td>{product.custom_label_1}</td>
                            <td>{product.custom_label_2}</td>
                            <td>{product.custom_label_3}</td>
                            <td>{product.custom_label_4}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
                    )}

                    <div className="pagination">
                        {Array.from({length: totalPages}, (_, i) => (
                            <button key={i} onClick={() => handlePageChange(i + 1)} disabled={i + 1 === page}>
                                {i + 1}
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </Layout>
);
};

export default Products;