/**
* Create by wenboling on 2018/6/7
*/
<template>
  <el-card class="box-card">
    <div slot="header" class="clearfix">
      <span style="font-weight: bold; font-size: larger;">{{ titleMap[selectedConfigFile] }}</span>
      <div  style="float: right;">
        <span style="font-size: 14px;color: #8c939d">当前配置文件>>&emsp;</span>
        <el-select v-model="selectedConfigFile" @change="selectedConfigFileChange" size="small">
          <el-option
            v-for="filename in filenames"
            :key="filename.value"
            :label="filename.label"
            :value="filename.value">
          </el-option>
        </el-select>
      </div>
    </div>
    <el-form label-width="250px" :model="constraints" v-if="selectedConfigFile==='swift'">
      <el-form-item label="Swift max file size"  style="font-weight: bold;">
        <el-row>
          <el-col :span="8">
            <el-input v-model="constraints.max_file_size" size="small"></el-input>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="20" class="comments">
            The largest "normal" object that can be saved in the cluster.
            This is also the limit on the size of each segment of a "large" object when using the large object manifest support.
            This value is set in bytes. Setting it to lower than 1MiB will cause some tests to fail. It is STRONGLY recommended to leave this value at the default (5 * 2**30 + 2).
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item label="Swift max meta name length" style="font-weight: bold;">
        <el-row>
          <el-col :span="8">
            <el-input v-model="constraints.max_meta_name_length" size="small"></el-input>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="20" class="comments">
            The max number of bytes in the utf8 encoding of the name portion of a metadata header.
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item label="Swift max meta value length" style="font-weight: bold;">
        <el-row>
          <el-col :span="8">
            <el-input v-model="constraints.max_meta_value_length" size="small"></el-input>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="20" class="comments">
            The max number of bytes in the utf8 encoding of a metadata value
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item label="Swift max max meta count" style="font-weight: bold;">
        <el-row>
          <el-col :span="8">
            <el-input v-model="constraints.max_meta_count" size="small"></el-input>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="20" class="comments">
            The max number of metadata keys that can be stored on a single account, container, or object
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item label="Swift max meta overall size" style="font-weight: bold;">
        <el-row>
          <el-col :span="8">
            <el-input v-model="constraints.max_meta_overall_size" size="small"></el-input>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="20" class="comments">
            The max number of bytes in the utf8 encoding of the metadata (keys + values)
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item label="Swift max header size" style="font-weight: bold;">
        <el-row>
          <el-col :span="8">
            <el-input v-model="constraints.max_header_size" size="small"></el-input>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="20" class="comments">
            the max number of bytes in the utf8 encoding of each header. Using 8192 as default because eventlet use 8192 as max size of
            header line. This value may need to be increased when using identity
            v3 API tokens including more than 7 catalog entries.
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item label="Swift extra header count" style="font-weight: bold;">
        <el-row>
          <el-col :span="8">
            <el-input v-model="constraints.extra_header_count" size="small"></el-input>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="20" class="comments">
            By default the maximum number of allowed headers depends on the number of max
            allowed metadata settings plus a default value of 36 for swift internally
            generated headers and regular http headers.  If for some reason this is not
            enough (custom middleware for example) it can be increased with the
            extra_header_count constraint.
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item label="Swift container listing limit" style="font-weight: bold;">
        <el-row>
          <el-col :span="8">
            <el-input v-model="constraints.container_listing_limit" size="small"></el-input>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="20" class="comments">
            The default (and max) number of items returned for a container listing request.
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item label="Swift account listing limit" style="font-weight: bold;">
        <el-row>
          <el-col :span="8">
            <el-input v-model="constraints.account_listing_limit" size="small"></el-input>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="20" class="comments">
            The default (and max) number of items returned for an account listing request
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item label="Swift max object name length" style="font-weight: bold;">
        <el-row>
          <el-col :span="8">
            <el-input v-model="constraints.max_object_name_length" size="small"></el-input>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="20" class="comments">
            The max number of bytes in the utf8 encoding of an object name
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item label="Swift max container name length" style="font-weight: bold;">
        <el-row>
          <el-col :span="8">
            <el-input v-model="constraints.max_container_name_length" size="small"></el-input>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="20" class="comments">
            The max number of bytes in the utf8 encoding of an account name
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item label="Swift max account name length" style="font-weight: bold;">
        <el-row>
          <el-col :span="8">
            <el-input v-model="constraints.max_account_name_length" size="small"></el-input>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="20" class="comments">
            The max number of bytes in the utf8 encoding of a container name
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item size="large">
        <el-button type="primary" @click="onSubmit">提交</el-button>
        <el-button>重置</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script>

  export default {
    data() {
      return {
        constraints: {
          max_file_size: '',
          max_meta_name_length: '',
          max_meta_value_length: '',
          max_meta_count: '',
          max_meta_overall_size: '',
          max_header_size: '',
          extra_header_count: '',
          max_object_name_length: '',
          container_listing_limit: '',
          account_listing_limit: '',
          max_account_name_length: '',
          max_container_name_length: '',
        },
        titleMap: {
          swift: "Swift Constraint Setting",
          rsync: "Rsync Setting",
          rsyslog: "Rsyslog Setting"
        },
        selectedConfigFile: "swift",
        filenames: [
          {
            value: "swift",
            label: "swift.conf"
          },
          {
            value: "rsync",
            label: "rsync.conf"
          },
          {
            value: "rsyslog",
            label: "rsyslog.conf"
          }
        ],
      }
    },
    created() {

    },
    mounted() {

    },
    methods: {
      onSubmit(){
        console.log("submit")
      },
      selectedConfigFileChange(){
        console.log("change")
      }
    }
  }
</script>
<style rel="stylesheet/scss" lang="scss" scoped>
  .clearfix:before,
  .clearfix:after {
    display: table;
    content: "";
  }
  .clearfix:after {
    clear: both
  }

  .box-card {
    width: 98%;
    margin: 10px auto;
  }
  .comments {
    background-color: #ecffeb;
    border-radius: 5px;
    padding: 8px;
    font-size: 14px;
    font-weight: lighter;
    line-height: 20px
  }
</style>
