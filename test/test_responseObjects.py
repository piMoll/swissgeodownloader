import unittest

from SwissGeoDownloader.api.responseObjects import File


class TestFileObject(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        pass
    
    @classmethod
    def tearDownClass(cls):
        pass
    
    def test_bbox_key_empty(self):
        file_obj = File(name="test_file", assetType="image",
                        href="http://example.com")
        self.assertEqual(file_obj.bboxKey, '')
    
    def test_bbox_key_valid(self):
        file_obj = File(name="test_file", assetType="image",
                        href="http://example.com")
        file_obj.setBbox([100.123456, 10.654321, 102.987654, 12.123456])
        self.assertEqual(file_obj.bboxKey, '100.1235|10.6543|102.9877|12.1235')
    
    def test_set_bbox_valid(self):
        file_obj = File(name="test_file", assetType="image",
                        href="http://example.com")
        bbox = [100.0, 10.0, 102.0, 12.0]
        file_obj.setBbox(bbox)
        self.assertEqual(file_obj.bbox, bbox)
    
    def test_set_bbox_invalid(self):
        file_obj = File(name="test_file", assetType="image",
                        href="http://example.com")
        # Invalid bbox length
        self.assertRaises(AssertionError, file_obj.setBbox, [1.0, 2.0, 3.0])
    
    def test_prop_key(self):
        file_obj = File(name="test_file", assetType="image",
                        href="http://example.com")
        file_obj.filetype = "image"
        file_obj.category = "jpeg"
        file_obj.resolution = "2.0"
        self.assertEqual(file_obj.propKey, 'image|jpeg|2.0')
    
    def test_isStreamable(self):
        file_obj = File('myTestFile', 'tiff', 'https://this.is.a.test.url')
        self.assertFalse(file_obj.isStreamable)
        file_obj.filetype = 'streamed tiff (COG)'
        self.assertTrue(file_obj.isStreamable)
    
    def test_timestamp_parsing(self):
        file_obj = File(name="test_file", assetType="image",
                        href="http://example.com")
        file_obj.setTimestamp("2023-07-16T12:34:56Z")
        self.assertEqual(file_obj.timestampStr, "2023-07-16")
        self.assertRaises(ValueError, file_obj.setTimestamp, 'this is a test')
    
    def test_timestamp_range_parsing(self):
        file_obj = File(name="test_file", assetType="image",
                        href="http://example.com")
        file_obj.setTimestamp('2023-07-16T12:34:56Z', '2024-07-16T12:34:56Z')
        self.assertEqual(file_obj.timestampStr, '2023-07-16 / 2024-07-16')
        self.assertRaises(ValueError, file_obj.setTimestamp,
                          '2023-07-16T12:34:56Z', 'this is a test')
    
    def test_timestamp_invalid(self):
        file_obj = File(name="test_file", assetType="image",
                        href="http://example.com")
        self.assertRaises(ValueError, file_obj.setTimestamp, '20-12-12T00:00')
        self.assertEqual(file_obj.timestampStr, '')
    
    def test_filetype_fits_filter(self):
        file_obj = File(name="test_file", assetType="image",
                        href="http://example.com")
        # If property is None, it should always pass the filter
        self.assertTrue(file_obj.filetypeFitsFilter(None))
        self.assertTrue(file_obj.filetypeFitsFilter("abc"))
        file_obj.filetype = "image"
        self.assertTrue(file_obj.filetypeFitsFilter(None))
        self.assertTrue(file_obj.filetypeFitsFilter("image"))
        self.assertTrue(file_obj.filetypeFitsFilter(""))
        self.assertFalse(file_obj.filetypeFitsFilter("video"))
    
    def test_category_fits_filter(self):
        file_obj = File(name="test_file", assetType="image",
                        href="http://example.com")
        # If property is None, it should always pass the filter
        self.assertTrue(file_obj.categoryFitsFilter(None))
        self.assertTrue(file_obj.categoryFitsFilter("abc"))
        file_obj.category = "jpeg"
        self.assertTrue(file_obj.categoryFitsFilter(None))
        self.assertTrue(file_obj.categoryFitsFilter("jpeg"))
        self.assertTrue(file_obj.categoryFitsFilter(""))
        self.assertFalse(file_obj.categoryFitsFilter("png"))
    
    def test_has_similar_bbox(self):
        file_obj = File(name="test_file", assetType="image",
                        href="http://example.com")
        file_obj.setBbox([100.0, 10.0, 102.0, 12.0])
        similar_bbox = [100.1, 10.1, 102.1, 12.1]
        self.assertTrue(file_obj.hasSimilarBboxAs(similar_bbox))
    
    def test_coordsys_fits_filter(self):
        file_obj = File(name="test_file", assetType="image",
                        href="http://example.com")
        # If property is None, it should always pass the filter
        self.assertTrue(file_obj.coordsysFitsFilter(None))
        self.assertTrue(file_obj.coordsysFitsFilter("abc"))
        file_obj.coordsys = "EPSG:4326"
        self.assertTrue(file_obj.coordsysFitsFilter(None))
        self.assertTrue(file_obj.coordsysFitsFilter("EPSG:4326"))
        self.assertTrue(file_obj.coordsysFitsFilter(""))
        self.assertFalse(file_obj.coordsysFitsFilter("EPSG:3857"))


if __name__ == '__main__':
    unittest.main()
